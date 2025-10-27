import os
import cv2
import time
import signal
import argparse
import threading
import numpy as np
from ultralytics import YOLO
from picamera2 import Picamera2
import paho.mqtt.client as mqtt

MODEL_PATH = "yolov8n.onnx"
FRAME_W, FRAME_H = 640, 480
MODEL_W, MODEL_H = 128, 128

CROP_BOTTOM = 50
CROP_RIGHT = 90

PAN_MIN, PAN_MAX = 0, 180
PAN_NEUTRAL = 90

PAN_RANGE_DEG = 35
PAN_LIMIT_MIN = max(PAN_MIN, PAN_NEUTRAL - PAN_RANGE_DEG)
PAN_LIMIT_MAX = min(PAN_MAX, PAN_NEUTRAL + PAN_RANGE_DEG)

KP_PAN = 1
SMOOTH_ALPHA = 0.0
MAX_STEP_DEG = 3
DEADZONE_PIX = 80

MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC_FOLLOW = "/follow"
MQTT_TOPIC_SERVO = "/servo"

PERSON_CONF_THRESH = 0.2
def clamp(val, min_val, max_val):
    return max(min_val, min(max_val, val))

def publish_follow(client, angle, topic):
    client.publish(topic, f"Body: {angle:.1f}")

def publish_wave(client, topic):
    client.publish(topic, "wave")

def has_display_env():
    return bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))
def main():
    parser = argparse.ArgumentParser(description="Publish follow angle to MQTT.")
    parser.add_argument("--gui", choices=["auto", "on", "off"], default="auto", help="Enable OpenCV UI.")
    parser.add_argument("--topic", default=MQTT_TOPIC_FOLLOW, help="MQTT topic to publish to.")
    parser.add_argument("--broker", default=MQTT_BROKER, help="MQTT broker host.")
    parser.add_argument("--port", type=int, default=MQTT_PORT, help="MQTT broker port.")
    args = parser.parse_args()

    gui = has_display_env() if args.gui == "auto" else (args.gui == "on")
    topic = args.topic

    stop_event = threading.Event()
    def _handle_stop(*_):
        stop_event.set()
    signal.signal(signal.SIGINT, _handle_stop)
    signal.signal(signal.SIGTERM, _handle_stop)

    sleeping = threading.Event()
    person_state = {
        "detected_before": False,
        "in_deadzone": False,
        "has_waved_for_current_target": False,
        "last_seen_time": None
    }

    PERSON_FORGET_TIME = 0.8

    client = mqtt.Client()
    def on_connect(c, userdata, flags, rc):
        try:
            c.subscribe("/sleep")
            print("Subscribed to /sleep")
        except Exception as e:
            print(f"Subscribe /sleep failed: {e}")

    def on_message(c, userdata, msg):
        payload = msg.payload.decode("utf-8", errors="ignore").strip().lower()
        if msg.topic == "/sleep":
            if payload.startswith("sleep:"):
                payload = payload.split(":", 1)[1].strip()
            if payload == "1":
                sleeping.set()
                person_state["detected_before"] = False
                person_state["in_deadzone"] = False
                person_state["has_waved_for_current_target"] = False
                person_state["last_seen_time"] = None
                print("Sleep=1 -> pause wave")
            elif payload == "0":
                sleeping.clear()
                person_state["detected_before"] = False
                person_state["in_deadzone"] = False
                person_state["has_waved_for_current_target"] = False
                person_state["last_seen_time"] = None
                print("Sleep=0 -> resume wave")

    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(args.broker, args.port)
        client.loop_start()
    except Exception as e:
        print(f"MQTT connect failed: {e}")
        return

    try:
        model = YOLO(MODEL_PATH, task="detect")
    except Exception as e:
        print(f"Model load failed: {e}")
        client.loop_stop()
        client.disconnect()
        return

    print("Using Raspberry Pi Camera (Picamera2)...")
    picam2 = Picamera2()
    cam_config = picam2.create_preview_configuration(
        main={"size": (FRAME_W, FRAME_H), "format": "RGB888"}
    )
    picam2.configure(cam_config)
    try:
        picam2.start()
    except Exception as e:
        print(f"Camera start failed: {e}")
        client.loop_stop()
        client.disconnect()
        return

    if gui:
        print("UI: enabled (press 'q' to quit).")
    else:
        print("UI: disabled (headless).")

    pan_angle = PAN_NEUTRAL
    window_ok = False
    person_detected_before = False

    try:
        while not stop_event.is_set():
            frame = picam2.capture_array()

            h, w = frame.shape[:2]
            frame = frame[0:h - CROP_BOTTOM, 0:w - CROP_RIGHT]
            curr_h, curr_w = frame.shape[:2]

            frame_resized = cv2.resize(frame, (MODEL_W, MODEL_H))
            results = model(frame_resized)

            boxes = []
            for det in results[0].boxes:
                cls = int(det.cls.cpu().numpy()) if hasattr(det, "cls") else int(det.cls)
                conf = float(det.conf.cpu().numpy()) if hasattr(det, "conf") else float(det.conf)
                if cls == 0 and conf >= PERSON_CONF_THRESH:
                    xyxy = det.xyxy[0].cpu().numpy()
                    boxes.append(xyxy)

            if boxes:
                boxes_sorted = sorted(boxes, key=lambda b: (b[2]-b[0])*(b[3]-b[1]), reverse=True)
                x1, y1, x2, y2 = boxes_sorted[0]

                scale_x = curr_w / MODEL_W
                scale_y = curr_h / MODEL_H
                x1, x2, y1, y2 = int(x1 * scale_x), int(x2 * scale_x), int(y1 * scale_y), int(y2 * scale_y)

                cx = (x1 + x2) // 2
                cy = (y1 + y2) // 2

                if gui:
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.circle(frame, (cx, cy), 4, (0, 0, 255), -1)

                err_x = cx - curr_w // 2
                velocity = 0 if abs(err_x) < DEADZONE_PIX else clamp(-err_x * KP_PAN, -MAX_STEP_DEG, MAX_STEP_DEG)
                pan_angle = SMOOTH_ALPHA * pan_angle + (1 - SMOOTH_ALPHA) * clamp(pan_angle + velocity, PAN_LIMIT_MIN, PAN_LIMIT_MAX)
                publish_follow(client, pan_angle, topic)

                currently_in_deadzone = abs(err_x) < DEADZONE_PIX
                
                if not sleeping.is_set():
                    if currently_in_deadzone and not person_state["has_waved_for_current_target"]:
                        print("Centered on person! Publishing wave command...")
                        publish_wave(client, MQTT_TOPIC_SERVO)
                        person_state["has_waved_for_current_target"] = True
                
                person_state["detected_before"] = True
                person_state["in_deadzone"] = currently_in_deadzone
                person_state["last_seen_time"] = time.time()
            else:
                if person_state["detected_before"]:
                    time_since_last_seen = time.time() - person_state["last_seen_time"] if person_state["last_seen_time"] else 999
                    
                    if time_since_last_seen > PERSON_FORGET_TIME:
                        print(f"No person detected for {PERSON_FORGET_TIME}s. Reset - waiting for next detection...")
                        person_state["detected_before"] = False
                        person_state["in_deadzone"] = False
                        person_state["has_waved_for_current_target"] = False
                        person_state["last_seen_time"] = None
                else:
                    person_state["last_seen_time"] = None

            if gui:
                try:
                    if not window_ok:
                        cv2.namedWindow("YOLO Smooth Stable 1D Tracking", cv2.WINDOW_NORMAL)
                        window_ok = True
                    
                    if person_state["in_deadzone"] and boxes:
                        status = "Centered"
                    elif person_state["detected_before"] and boxes:
                        status = "Tracking"
                    elif person_state["detected_before"] and not boxes:
                        time_since = time.time() - person_state["last_seen_time"] if person_state["last_seen_time"] else 0
                        status = f"Lost ({PERSON_FORGET_TIME - time_since:.1f}s)"
                    else:
                        status = "Waiting"
                    
                    cv2.putText(frame, f"Pan:{pan_angle:.1f} [{status}]", (6, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                    cv2.imshow("YOLO Smooth Stable 1D Tracking", frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        stop_event.set()
                except cv2.error as e:
                    print(f"Disabling UI (OpenCV error: {e})")
                    gui = False
                    try:
                        cv2.destroyAllWindows()
                    except Exception:
                        pass
            else:
                time.sleep(0.005)
    finally:
        try:
            picam2.stop()
        except Exception:
            pass
        try:
            if gui:
                cv2.destroyAllWindows()
        except Exception:
            pass
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()