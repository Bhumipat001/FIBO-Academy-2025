import serial
import paho.mqtt.client as mqtt
import time
import threading
import RPi.GPIO as GPIO

MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC_TOUCH = "/touch"
MQTT_TOPIC_SERVO = "/servo"
MQTT_TOPIC_LIGHT = "/light"
MQTT_TOPIC_RADAR = "/radar"
MQTT_TOPIC_HAPTIC = "/haptic"
MQTT_TOPIC_FOLLOW = "/follow"
MQTT_TOPIC_SLEEP = "/sleep"
MQTT_TOPIC_LIGHTBASE = "/LightBase"

SERIAL_PORT = "/dev/serial0"
SERIAL_BAUD = 115200

BOOT_GPIO_PIN = 18


def on_connect(client, userdata, flags, reasonCode, properties=None):
    try:
        code = int(reasonCode)
    except Exception:
        code = reasonCode
    print(f"Connected to MQTT broker with result code: {code}")
    client.subscribe(MQTT_TOPIC_SERVO)
    print(f"Subscribed to topic: {MQTT_TOPIC_SERVO}")
    client.subscribe(MQTT_TOPIC_LIGHT)
    print(f"Subscribed to topic: {MQTT_TOPIC_LIGHT}")
    client.subscribe(MQTT_TOPIC_HAPTIC)
    print(f"Subscribed to topic: {MQTT_TOPIC_HAPTIC}")
    client.subscribe(MQTT_TOPIC_FOLLOW)
    print(f"Subscribed to topic: {MQTT_TOPIC_FOLLOW}")
    client.subscribe(MQTT_TOPIC_SLEEP)
    print(f"Subscribed to topic: {MQTT_TOPIC_SLEEP}")
    client.subscribe(MQTT_TOPIC_LIGHTBASE)
    print(f"Subscribed to topic: {MQTT_TOPIC_LIGHTBASE}")

    if userdata.get("sleeping"):
        try:
            client.unsubscribe(MQTT_TOPIC_FOLLOW)
            print(f"Sleeping on connect -> unsubscribed from {MQTT_TOPIC_FOLLOW}")
        except Exception as e:
            print(f"Failed to unsubscribe on connect: {e}")

def on_message(client, userdata, msg):
    ser = userdata["serial"]
    lock = userdata["lock"]
    sleeping = userdata.get("sleeping", False)
    message = msg.payload.decode("utf-8").strip()
    print(f"Received MQTT message on {msg.topic}: {message}")

    if msg.topic == MQTT_TOPIC_SERVO:
        data = f"Servo: {message}\n".encode("utf-8")
        try:
            with lock:
                ser.write(data)
            print(f"Forwarded to serial: Servo: {message}")
        except Exception as e:
            print(f"Failed to write to serial: {e}")
    elif msg.topic == MQTT_TOPIC_LIGHT:
        data = f"Light: {message}\n".encode("utf-8")
        try:
            with lock:
                ser.write(data)
            print(f"Forwarded to serial: Light: {message}")
        except Exception as e:
            print(f"Failed to write to serial: {e}")
    elif msg.topic == MQTT_TOPIC_HAPTIC:
        data = f"Haptic: {message}\n".encode("utf-8")
        try:
            with lock:
                ser.write(data)
            print(f"Forwarded to serial: Haptic: {message}")
        except Exception as e:
            print(f"Failed to write to serial: {e}")
    elif msg.topic == MQTT_TOPIC_LIGHTBASE:
        data = f"LightBase: {message}\n".encode("utf-8")
        try:
            with lock:
                ser.write(data)
            print(f"Forwarded to serial: LightBase: {message}")
        except Exception as e:
            print(f"Failed to write to serial: {e}")
    elif msg.topic == MQTT_TOPIC_FOLLOW:
        if userdata.get("sleeping", False):
            print("Sleeping -> ignoring /follow message")
            return
        data = f"{message}\n".encode("utf-8")
        try:
            with lock:
                ser.write(data)
            print(f"Forwarded to serial: {message}")
        except Exception as e:
            print(f"Failed to write to serial: {e}")
    elif msg.topic == MQTT_TOPIC_SLEEP:
        data = f"Sleep: {message}\n".encode("utf-8")
        try:
            with lock:
                ser.write(data)
            print(f"Forwarded to serial: Sleep: {message}")
        except Exception as e:
            print(f"Failed to write to serial: {e}")

        cmd = message.strip()
        if cmd == "1" and not sleeping:
            userdata["sleeping"] = True
            try:
                client.unsubscribe(MQTT_TOPIC_FOLLOW)
                print(f"Sleep=1 -> unsubscribed from {MQTT_TOPIC_FOLLOW} (paused pan tracking)")
            except Exception as e:
                print(f"Failed to unsubscribe {MQTT_TOPIC_FOLLOW}: {e}")
        elif cmd == "0" and sleeping:
            userdata["sleeping"] = False
            try:
                client.subscribe(MQTT_TOPIC_FOLLOW)
                print(f"Sleep=0 -> subscribed to {MQTT_TOPIC_FOLLOW} (resumed pan tracking)")
            except Exception as e:
                print(f"Failed to subscribe {MQTT_TOPIC_FOLLOW}: {e}")


def serial_to_mqtt(ser, client, lock):
    while True:
        try:
            if ser.in_waiting:
                with lock:
                    line = ser.readline().decode("utf-8").strip()
                if line:
                    print(f"Received from serial: {line}")
                    if line.startswith("Touch:"):
                        client.publish(MQTT_TOPIC_TOUCH, line)
                        print(f"Published to {MQTT_TOPIC_TOUCH}: {line}")
                    elif line.startswith("Radar:"):
                        client.publish(MQTT_TOPIC_RADAR, line)
                        print(f"Published to {MQTT_TOPIC_RADAR}: {line}")
            time.sleep(0.01)
        except serial.SerialException as e:
            print(f"Serial error: {e}")
            break
        except Exception as e:
            print(f"Error in serial loop: {e}")
            time.sleep(1)


def main():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BOOT_GPIO_PIN, GPIO.OUT)
    GPIO.output(BOOT_GPIO_PIN, GPIO.LOW)
    
    print("Waiting 5 seconds before activating boot signal...")
    time.sleep(1)
    
    GPIO.output(BOOT_GPIO_PIN, GPIO.HIGH)
    print(f"GPIO{BOOT_GPIO_PIN} set HIGH (boot signal active)")

    try:
        ser = serial.Serial(SERIAL_PORT, SERIAL_BAUD, timeout=1)
        print(f"Connected to {SERIAL_PORT} at {SERIAL_BAUD} baud")
    except serial.SerialException as e:
        print(f"Failed to open serial port: {e}")
        GPIO.output(BOOT_GPIO_PIN, GPIO.LOW)
        GPIO.cleanup()
        return

    lock = threading.Lock()

    client = mqtt.Client(
        protocol=mqtt.MQTTv5,
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        userdata={"serial": ser, "lock": lock, "sleeping": False},
    )
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(MQTT_BROKER, MQTT_PORT)
        client.loop_start()
    except Exception as e:
        print(f"Failed to connect to MQTT broker: {e}")
        ser.close()
        GPIO.output(BOOT_GPIO_PIN, GPIO.LOW)
        GPIO.cleanup()
        return

    thread = threading.Thread(target=serial_to_mqtt, args=(ser, client, lock), daemon=True)
    thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        ser.close()
        client.loop_stop()
        client.disconnect()
        GPIO.output(BOOT_GPIO_PIN, GPIO.LOW)
        GPIO.cleanup()
        print(f"GPIO{BOOT_GPIO_PIN} set LOW (boot signal inactive)")


if __name__ == "__main__":
    main()