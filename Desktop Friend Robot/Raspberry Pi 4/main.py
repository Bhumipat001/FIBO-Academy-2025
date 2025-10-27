import threading
import time
import paho.mqtt.client as mqtt

MQTT_BROKER = "localhost"
MQTT_PORT = 1883

TOPIC_TOUCH = "/touch"
TOPIC_HAPTIC = "/haptic"
TOPIC_SERVO = "/servo"
TOPIC_SCREEN = "/screen"
TOPIC_RADAR = "/radar"
TOPIC_SOUND = "/sound"
TOPIC_SLEEP = "/sleep"

class HeadState:
    def __init__(self):
        self.lock = threading.Lock()
        self.head_active_now = False
        self.active = False
        self.off_timer = None
        self.radar_active = False
        self.radar_off_timer = None
        self.radar_blocked = False
        self.radar_block_timer = None
        self.sleeping = False
        self.inactivity_timer = None
        self.radar_subscribed = True

def parse_touch_payload(payload: str):
    try:
        s = payload.strip()
        if s.lower().startswith("touch:"):
            s = s.split(":", 1)[1].strip()
        parts = [p.strip() for p in s.split(",") if p.strip()]
        result = {}
        for part in parts:
            if "=" in part:
                k, v = part.split("=", 1)
                result[k.strip()] = int(v.strip())
        return result
    except Exception:
        return {}

def on_connect(client, userdata, flags, reasonCode, properties=None):
    try:
        code = int(reasonCode)
    except Exception:
        code = reasonCode
    print(f"Connected to MQTT broker with result code: {code}")
    client.subscribe(TOPIC_TOUCH)
    print(f"Subscribed to topic: {TOPIC_TOUCH}")
    client.subscribe(TOPIC_SLEEP)
    print(f"Subscribed to topic: {TOPIC_SLEEP}")
    client.subscribe(TOPIC_RADAR)
    print(f"Subscribed to topic: {TOPIC_RADAR}")
    userdata.radar_subscribed = True

def on_message(client, userdata: HeadState, msg):
    if msg.topic == TOPIC_TOUCH:
        handle_touch(client, userdata, msg)
    elif msg.topic == TOPIC_RADAR:
        handle_radar(client, userdata, msg)
    elif msg.topic == TOPIC_SLEEP:
        handle_sleep(client, userdata, msg)

def wake_if_sleeping(client, st: HeadState):
    if st.sleeping:
        client.publish(TOPIC_SLEEP, "0")
        print("Waking from sleep -> sleep=0")
        st.sleeping = False
        if not st.radar_subscribed:
            client.subscribe(TOPIC_RADAR)
            st.radar_subscribed = True
            print(f"Subscribed to topic: {TOPIC_RADAR}")

def update_inactivity_timer(client, st: HeadState):
    idle = not st.head_active_now
    if idle:
        if st.inactivity_timer is None:
            def go_sleep():
                with st.lock:
                    if (not st.head_active_now) and (not st.sleeping):
                        client.publish(TOPIC_SLEEP, "1")
                        print("Inactivity 3m -> sleep=1")
                        st.sleeping = True
                        if st.radar_subscribed:
                            client.unsubscribe(TOPIC_RADAR)
                            st.radar_subscribed = False
                            print(f"Unsubscribed from topic: {TOPIC_RADAR}")
                    st.inactivity_timer = None
            st.inactivity_timer = threading.Timer(180.0, go_sleep)
            st.inactivity_timer.daemon = True
            st.inactivity_timer.start()
    else:
        if st.inactivity_timer:
            st.inactivity_timer.cancel()
            st.inactivity_timer = None

def handle_sleep(client, userdata: HeadState, msg):
    payload = msg.payload.decode("utf-8", errors="ignore").strip().lower()
    try:
        if payload.startswith("sleep:"):
            val = payload.split(":", 1)[1].strip()
        else:
            val = payload
        new_state = (val == "1")
    except Exception:
        return

    st = userdata
    with st.lock:
        prev = st.sleeping
        st.sleeping = new_state
        if new_state:
            if st.inactivity_timer:
                st.inactivity_timer.cancel()
                st.inactivity_timer = None
            if st.radar_subscribed:
                client.unsubscribe(TOPIC_RADAR)
                st.radar_subscribed = False
                print(f"Unsubscribed from topic: {TOPIC_RADAR}")
        else:
            if not st.radar_subscribed:
                client.subscribe(TOPIC_RADAR)
                st.radar_subscribed = True
                print(f"Subscribed to topic: {TOPIC_RADAR}")
            update_inactivity_timer(client, st)
        if new_state != prev:
            print(f"/sleep received -> sleeping={st.sleeping}")

def handle_touch(client, userdata: HeadState, msg):
    payload = msg.payload.decode("utf-8", errors="ignore").strip()
    values = parse_touch_payload(payload)
    L_HEAD = int(values.get("L_HEAD", 0))
    R_HEAD = int(values.get("R_HEAD", 0))
    head_now = (L_HEAD == 1) or (R_HEAD == 1)

    st = userdata
    with st.lock:
        st.head_active_now = head_now

        if head_now:
            wake_if_sleeping(client, st)

            if st.off_timer:
                st.off_timer.cancel()
                st.off_timer = None

            if not st.active:
                client.publish(TOPIC_HAPTIC, "1")
                client.publish(TOPIC_SERVO, "ear1")
                client.publish(TOPIC_SCREEN, "happy")
                client.publish(TOPIC_SOUND, "meow")
                st.active = True
                print("Head touch detected -> haptic=1, servo='ear1', screen='happy', sound='meow'")
            elif st.radar_active:
                client.publish(TOPIC_SCREEN, "happy")
                print("Touch overrides radar -> screen='happy'")
        else:
            if st.off_timer:
                st.off_timer.cancel()

            def do_off():
                with st.lock:
                    if not st.head_active_now and st.active:
                        client.publish(TOPIC_HAPTIC, "0")
                        client.publish(TOPIC_SERVO, "ear0")
                        client.publish(TOPIC_SCREEN, "normal")
                        print("Head released 3s -> haptic=0, servo='ear0', screen='normal'")
                        st.active = False
                        
                        st.radar_blocked = True
                        if st.radar_block_timer:
                            st.radar_block_timer.cancel()
                        
                        def unblock_radar():
                            with st.lock:
                                st.radar_blocked = False
                                st.radar_block_timer = None
                                if st.radar_active and not st.active:
                                    client.publish(TOPIC_SCREEN, "dizzy")
                                    print("Radar unblocked and still active -> screen='dizzy'")
                                else:
                                    print("Radar unblocked after touch cooldown")
                        
                        st.radar_block_timer = threading.Timer(3.0, unblock_radar)
                        st.radar_block_timer.daemon = True
                        st.radar_block_timer.start()
                    st.off_timer = None

            st.off_timer = threading.Timer(3.0, do_off)
            st.off_timer.daemon = True
            st.off_timer.start()

        update_inactivity_timer(client, st)

def handle_radar(client, userdata: HeadState, msg):
    payload = msg.payload.decode("utf-8", errors="ignore").strip()
    
    radar_state = 0
    try:
        if payload.lower().startswith("radar:"):
            radar_state = int(payload.split(":", 1)[1].strip())
        else:
            radar_state = int(payload)
    except Exception:
        return

    st = userdata
    with st.lock:
        if radar_state == 1:
            wake_if_sleeping(client, st)

            if st.radar_off_timer:
                st.radar_off_timer.cancel()
                st.radar_off_timer = None

            if not st.radar_active:
                st.radar_active = True
                if not st.active and not st.radar_blocked:
                    client.publish(TOPIC_SCREEN, "dizzy")
                    print("Radar detected -> screen='dizzy'")
                elif st.radar_blocked:
                    print("Radar detected but blocked (touch cooldown) -> no action")
                else:
                    print("Radar detected but touch active -> keeping screen='happy'")
        else:
            if st.radar_off_timer:
                st.radar_off_timer.cancel()

            def do_radar_off():
                with st.lock:
                    if st.radar_active:
                        st.radar_active = False
                        if not st.active:
                            client.publish(TOPIC_SCREEN, "normal")
                            print("Radar cleared 3s -> screen='normal'")
                        else:
                            print("Radar cleared but touch active -> keeping screen='happy'")
                    st.radar_off_timer = None

            st.radar_off_timer = threading.Timer(3.0, do_radar_off)
            st.radar_off_timer.daemon = True
            st.radar_off_timer.start()

def main():
    state = HeadState()

    client = mqtt.Client(
        protocol=mqtt.MQTTv5,
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        userdata=state,
    )
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(MQTT_BROKER, MQTT_PORT)
    client.loop_start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        with state.lock:
            if state.off_timer:
                state.off_timer.cancel()
                state.off_timer = None
            if state.radar_off_timer:
                state.radar_off_timer.cancel()
                state.radar_off_timer = None
            if state.radar_block_timer:
                state.radar_block_timer.cancel()
                state.radar_block_timer = None
            if state.inactivity_timer:
                state.inactivity_timer.cancel()
                state.inactivity_timer = None
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()