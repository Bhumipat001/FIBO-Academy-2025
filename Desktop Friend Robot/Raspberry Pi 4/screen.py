import board
import digitalio
from adafruit_rgb_display import ili9341
from PIL import Image, ImageOps, ImageSequence
import time
import paho.mqtt.client as mqtt
import threading
import sys
import os

spi = board.SPI()
dc = digitalio.DigitalInOut(board.D24)
cs = digitalio.DigitalInOut(board.CE0)
reset = digitalio.DigitalInOut(board.D25)
display = ili9341.ILI9341(spi, cs=cs, dc=dc, rst=reset, baudrate=32000000)

dir_folder = os.path.expanduser("~/RobotFriend/screen/")
gif_directory = dir_folder
gif_files = {}

for filename in os.listdir(gif_directory):
    if filename.endswith(".gif"):
        gif_name = filename[:-4]
        gif_files[gif_name] = Image.open(os.path.join(gif_directory, filename))

current_file = "normal" if "normal" in gif_files else None
file_type = "gif"
is_sleeping = False

LIGHT_TOPIC = "/light"
LIGHT_NORMAL_PAYLOAD = "Hex(B5B5B5) Brightness(100) Fade(0)"
LIGHT_DIZZY_PAYLOAD = "Hex(00FF00) Brightness(100) Fade(1)"
LIGHT_HAPPY_PAYLOAD = "Hex(E0822D) Brightness(100) Fade(0)"
LIGHT_SLEEP_PAYLOAD = "Hex(0000FF) Brightness(100) Fade(1)"

def publish_light_normal():
    global client
    try:
        client.publish(LIGHT_TOPIC, LIGHT_NORMAL_PAYLOAD)
    except Exception as e:
        print(f"Light publish failed: {e}")

def publish_light_dizzy():
    global client
    try:
        client.publish(LIGHT_TOPIC, LIGHT_DIZZY_PAYLOAD)
    except Exception as e:
        print(f"Light publish failed: {e}")

def publish_light_happy():
    global client
    try:
        client.publish(LIGHT_TOPIC, LIGHT_HAPPY_PAYLOAD)
    except Exception as e:
        print(f"Light publish failed: {e}")

def publish_light_sleep():
    global client
    try:
        client.publish(LIGHT_TOPIC, LIGHT_SLEEP_PAYLOAD)
    except Exception as e:
        print(f"Light publish failed: {e}")

stop_event = threading.Event()
lock = threading.Lock()
running = True

def on_connect(client, userdata, flags, reasonCode, properties=None):
    try:
        code = int(reasonCode)
    except Exception:
        code = reasonCode
    print(f"Connected with result code: {code}")
    client.subscribe("/screen")
    client.subscribe("/sleep")

def on_message(client, userdata, msg):
    global current_file, file_type, stop_event, is_sleeping
    payload = msg.payload.decode().strip().lower()

    if msg.topic == "/sleep":
        if payload == "1":
            is_sleeping = True
            if "sleep" in gif_files:
                with lock:
                    current_file = "sleep"
                    file_type = "gif"
                    stop_event.set()
                publish_light_sleep()
        elif payload == "0":
            is_sleeping = False
            if "normal" in gif_files:
                with lock:
                    current_file = "normal"
                    file_type = "gif"
                    stop_event.set()
                publish_light_normal()
        return

    if msg.topic == "/screen":
        if is_sleeping:
            return
        if payload in gif_files:
            with lock:
                current_file = payload
                file_type = "gif"
                stop_event.set()
            if payload == "normal":
                publish_light_normal()
            elif payload == "dizzy":
                publish_light_dizzy()
            elif payload == "happy":
                publish_light_happy()
            elif payload == "sleep":
                publish_light_sleep()

client = mqtt.Client(
    protocol=mqtt.MQTTv5,
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
    userdata=None
)
client.on_connect = on_connect
client.on_message = on_message
client.connect("localhost", 1883)
client.loop_start()

def process_frame(frame):
    frame = frame.convert("RGB")
    r, g, b = frame.split()
    frame = Image.merge("RGB", (r, g, b))
    frame = frame.rotate(270, expand=True)
    frame = ImageOps.invert(frame)
    frame = frame.resize((display.width, display.height))
    return frame

def responsive_sleep(duration):
    step = 0.01
    elapsed = 0
    while running and elapsed < duration:
        time.sleep(min(step, duration - elapsed))
        elapsed += step

def display_gif(img):
    target_frame_time = 1.0 / 60.0
    for frame in ImageSequence.Iterator(img):
        if not running or stop_event.is_set():
            stop_event.clear()
            break
        start = time.time()
        frame = process_frame(frame)
        display.image(frame)
        duration = frame.info.get('duration', 50) / 1000
        sleep_time = max(target_frame_time, duration)
        elapsed = time.time() - start
        remaining = sleep_time - elapsed
        if remaining > 0:
            responsive_sleep(remaining)

try:
    with lock:
        img = gif_files["normal"]
    publish_light_normal()
    display_gif(img)

    while running:
        with lock:
            img = gif_files[current_file]

        if file_type == "gif":
            display_gif(img)
        else:
            frame = process_frame(img)
            display.image(frame)
            responsive_sleep(0.1)

except KeyboardInterrupt:
    print("\nExiting...")
finally:
    running = False
    client.loop_stop()
    client.disconnect()
    sys.exit(0)