import os
import subprocess
import time
import shutil
from glob import glob
import paho.mqtt.client as mqtt

MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC_SOUND = "/sound"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SOUND_FOLDER = os.path.join(BASE_DIR, "sound")

SOUND_EXTENSIONS = [".wav"]


def log(msg):
    print(msg, flush=True)


def find_aplay():
    for p in ("/usr/bin/aplay", "/bin/aplay", "/usr/local/bin/aplay"):
        if os.path.exists(p):
            return p
    return shutil.which("aplay")


APLAY = find_aplay()


def list_available_sounds():
    files = []
    for ext in SOUND_EXTENSIONS:
        files.extend(glob(os.path.join(SOUND_FOLDER, f"*{ext}")))
    return sorted(os.path.basename(f) for f in files)


def resolve_sound_path(name: str) -> str | None:
    if not name:
        return None

    name = os.path.basename(name).strip()
    lower = name.lower()
    base, ext = os.path.splitext(lower)

    candidates = []

    if ext:
        exact = os.path.join(SOUND_FOLDER, name)
        candidates.append(exact)
        for fname in os.listdir(SOUND_FOLDER):
            if fname.lower() == lower:
                candidates.append(os.path.join(SOUND_FOLDER, fname))
    else:
        for fname in os.listdir(SOUND_FOLDER):
            fbase, fext = os.path.splitext(fname)
            if fbase.lower() == base and fext.lower() in SOUND_EXTENSIONS:
                candidates.append(os.path.join(SOUND_FOLDER, fname))

    for path in candidates:
        if os.path.exists(path):
            return path
    return None


def on_connect(client, userdata, flags, reasonCode, properties=None):
    try:
        code = int(reasonCode)
    except Exception:
        code = reasonCode
    log(f"Connected to MQTT broker with result code: {code}")
    client.subscribe(MQTT_TOPIC_SOUND)
    log(f"Subscribed to topic: {MQTT_TOPIC_SOUND}")


def on_message(client, userdata, msg):
    sound_name = msg.payload.decode("utf-8").strip()
    log(f"Received MQTT message on {msg.topic}: {sound_name}")

    if not os.path.isdir(SOUND_FOLDER):
        log(f"Sound folder not found: {SOUND_FOLDER}")
        return

    path = resolve_sound_path(sound_name)
    if not path:
        log(f"Sound file not found for payload '{sound_name}'. "
            f"Available: {list_available_sounds()}")
        return

    if not APLAY:
        log("Audio player 'aplay' not found. Install with: sudo apt-get install alsa-utils")
        return

    log(f"Playing sound: {path}")
    try:
        subprocess.run([APLAY, "-q", path], check=True)
        log(f"Finished playing: {path}")
    except subprocess.CalledProcessError as e:
        log(f"Audio player returned error: {e}")
    except FileNotFoundError:
        log("Audio player not found. Install with: sudo apt-get install alsa-utils")
    except Exception as e:
        log(f"Error playing sound: {e}")


def main():
    if not os.path.exists(SOUND_FOLDER):
        os.makedirs(SOUND_FOLDER, exist_ok=True)
        log(f"Created sound folder: {SOUND_FOLDER}")

    log(f"Using SOUND_FOLDER={SOUND_FOLDER}")
    log(f"Available sounds: {list_available_sounds()}")
    log(f"Using aplay at: {APLAY if APLAY else 'NOT FOUND'}")

    client = mqtt.Client(
        protocol=mqtt.MQTTv5,
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
    )
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(MQTT_BROKER, MQTT_PORT)
        log(f"Connecting to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}...")
    except Exception as e:
        log(f"Failed to connect to MQTT broker: {e}")
        return

    try:
        log("Sound player started. Press Ctrl+C to exit.")
        client.loop_forever()
    except KeyboardInterrupt:
        log("\nExiting...")
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()