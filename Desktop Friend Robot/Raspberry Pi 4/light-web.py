#!/usr/bin/env python3
import json
import re
import time
import os
import web
import paho.mqtt.client as mqtt

MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC_LIGHTBASE = "/LightBase"
urls = (
    "/", "Index",
    "/api/lightbase", "LightBaseAPI",
    "/api/shutdown", "ShutdownAPI",
)

mqtt_connected = False
mqtt_last_error = None

def on_connect(client, userdata, flags, reasonCode, properties=None):
    global mqtt_connected
    def ok(rc):
        try:
            return int(rc) == 0
        except Exception:
            return str(rc).lower() in ("0", "success")
    mqtt_connected = ok(reasonCode)
    print(f"[MQTT] Connected: {mqtt_connected} code={reasonCode}")

def on_disconnect(client, userdata, reasonCode, properties=None):
    global mqtt_connected
    mqtt_connected = False
    print(f"[MQTT] Disconnected code={reasonCode}")

def init_mqtt():
    global mqtt_last_error
    client = mqtt.Client(
        protocol=mqtt.MQTTv5,
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2
    )
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, keepalive=30)
        client.loop_start()
    except Exception as e:
        mqtt_last_error = str(e)
        print(f"[MQTT] Connect error: {e}")
    return client

mqtt_client = init_mqtt()

def publish_lightbase(message: str):
    if not message or not isinstance(message, str):
        raise ValueError("Invalid message")
    info = mqtt_client.publish(MQTT_TOPIC_LIGHTBASE, message, qos=0, retain=False)
    return {"mid": info.mid}

PAGE_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>LightBase Controller</title>
<style>
  :root {
    --bg: #0b1220;
    --panel: #111a2b;
    --panel-2: #0e1727;
    --accent: #2b7cff;
    --accent-2: #69a1ff;
    --text: #e6efff;
    --muted: #9db4d6;
    --danger: #ff5f6d;
    --ok: #33d17a;
    --btn: #14213a;
    --btn-hover: #1b2a4d;
    --shadow: rgba(0,0,0,0.35);
  }
  * { box-sizing: border-box; }
  body {
    margin: 0; background: radial-gradient(1200px 600px at 70% -10%, #13203b 0%, var(--bg) 50%),
                       linear-gradient(180deg, #0b1220 0%, #0a101c 100%);
    color: var(--text); font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, "Helvetica Neue", Arial, "Noto Sans", "Apple Color Emoji", "Segoe UI Emoji";
    min-height: 100vh; display: grid; place-items: center; padding: 24px;
  }
  .wrap {
    width: min(920px, 96vw);
    position: relative;
  }
  .shutdown-btn {
    position: absolute;
    top: -50px;
    right: 0;
    appearance: none;
    border: 1px solid #5b2932;
    background: linear-gradient(180deg, #6a2c37 0%, #4a1f27 100%);
    color: var(--text);
    border-radius: 10px;
    padding: 8px 16px;
    font-weight: 600;
    cursor: pointer;
    font-size: 14px;
    transition: transform 0.02s ease, background 0.2s;
    box-shadow: 0 6px 16px rgba(16,28,56,0.6), inset 0 1px 0 rgba(255,255,255,0.05);
  }
  .shutdown-btn:hover {
    background: linear-gradient(180deg, #7a3240 0%, #53232c 100%);
  }
  .shutdown-btn:active {
    transform: translateY(1px);
  }
  .card {
    background: linear-gradient(180deg, var(--panel) 0%, var(--panel-2) 100%);
    border: 1px solid #1a2842; border-radius: 16px; padding: 20px;
    box-shadow: 0 12px 30px var(--shadow), inset 0 1px 0 rgba(255,255,255,0.03);
  }
  h1 { margin: 0 0 6px 0; font-size: 28px; letter-spacing: 0.3px; }
  .sub { color: var(--muted); margin-bottom: 18px; }
  .grid {
    display: grid; gap: 16px;
    grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  }
  .panel {
    background: #0c1528; border: 1px solid #1a2842; border-radius: 12px; padding: 16px;
  }
  .panel h3 { margin: 0 0 10px 0; font-size: 16px; color: var(--accent-2); }
  .row { display: flex; align-items: center; gap: 10px; margin: 10px 0; }
  .btn {
    appearance: none; border: 1px solid #29406e; color: var(--text);
    background: linear-gradient(180deg, #1a2b4c 0%, #14213a 100%); border-radius: 10px;
    padding: 10px 14px; font-weight: 600; cursor: pointer; transition: transform 0.02s ease, background 0.2s, border-color 0.2s;
    box-shadow: 0 6px 16px rgba(16,28,56,0.6), inset 0 1px 0 rgba(255,255,255,0.05);
  }
  .btn:hover { background: linear-gradient(180deg, #22365f 0%, #182845 100%); }
  .btn:active { transform: translateY(1px); }
  .btn-danger { border-color: #5b2932; background: linear-gradient(180deg, #6a2c37 0%, #4a1f27 100%); }
  .btn-danger:hover { background: linear-gradient(180deg, #7a3240 0%, #53232c 100%); }
  .btn-accent { border-color: #2b7cff; background: linear-gradient(180deg, #2b7cff 0%, #1f5ccc 100%); }
  .btn-accent:hover { background: linear-gradient(180deg, #3b8aff 0%, #2a67d6 100%); }
  .slider { width: 100%; }
  .label { color: var(--muted); font-size: 12px; }
  input[type="color"] {
    width: 48px; height: 36px; border: 1px solid #29406e; background: #0c1528; border-radius: 8px; padding: 0;
  }
  input[type="checkbox"] { width: 18px; height: 18px; accent-color: var(--accent); }
  .status {
    display: flex; align-items: center; gap: 8px;
    padding: 8px 12px; border-radius: 10px; background: #0c1528; border: 1px solid #1a2842; color: var(--muted);
  }
  .dot { width: 10px; height: 10px; border-radius: 50%; background: #999; box-shadow: 0 0 0 3px rgba(0,0,0,0.2) inset; }
  .ok { background: var(--ok); }
  .err { background: var(--danger); }
  .toast {
    position: fixed; bottom: 20px; right: 20px; padding: 10px 14px; border-radius: 10px;
    background: #0c1528; border: 1px solid #1a2842; color: var(--text);
    box-shadow: 0 12px 30px var(--shadow); opacity: 0; transform: translateY(8px);
    transition: opacity .2s ease, transform .2s ease;
  }
  .toast.show { opacity: 1; transform: translateY(0); }
  .footer { margin-top: 14px; display: flex; justify-content: space-between; align-items: center; color: var(--muted); font-size: 12px; }
  code { background: #0c1528; border: 1px solid #1a2842; border-radius: 6px; padding: 2px 6px; }
  .modal {
    display: none;
    position: fixed;
    z-index: 1000;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0,0,0,0.7);
    justify-content: center;
    align-items: center;
  }
  .modal.show { display: flex; }
  .modal-content {
    background: var(--panel);
    border: 1px solid #1a2842;
    border-radius: 16px;
    padding: 24px;
    max-width: 400px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.5);
  }
  .modal-content h2 { margin: 0 0 12px 0; color: var(--danger); }
  .modal-content p { margin: 0 0 20px 0; color: var(--muted); }
  .modal-buttons { display: flex; gap: 10px; justify-content: flex-end; }
</style>
</head>
<body>
  <div class="wrap">
    <button class="shutdown-btn" id="btnShutdown">⏻ Shutdown Pi</button>
    
    <div class="card">
      <h1>LightBase Controller</h1>
      <div class="sub">Publish commands to MQTT topic <code>/LightBase</code></div>

      <div class="grid">
        <div class="panel">
          <h3>Power</h3>
          <div class="row">
            <button class="btn btn-danger" id="btnOff">Turn Off</button>
          </div>
          <div class="label">Sends: <code>off</code></div>
        </div>

        <div class="panel">
          <h3>Rainbow</h3>
          <div class="row">
            <input id="rainbowBrightness" class="slider" type="range" min="0" max="100" value="100" />
            <span><span id="rbv">100</span>%</span>
          </div>
          <div class="row">
            <button class="btn btn-accent" id="btnRainbow">Set Rainbow</button>
          </div>
          <div class="label">Sends: <code>rainbow [Brightness]</code> e.g. <code>rainbow 100</code></div>
        </div>

        <div class="panel">
          <h3>Static Color</h3>
          <div class="row">
            <label class="label">Color</label>
            <input id="colorHex" type="color" value="#ffb126" />
            <label class="label">Brightness</label>
            <input id="colorBrightness" class="slider" type="range" min="0" max="100" value="100" />
            <span><span id="cbv">100</span>%</span>
          </div>
          <div class="row">
            <label class="label">Fade</label>
            <input id="fadeToggle" type="checkbox" />
            <button class="btn" id="btnColor">Set Color</button>
          </div>
          <div class="label">Sends: <code>Hex(RRGGBB) Brightness(0-100) Fade(0|1)</code></div>
        </div>
      </div>

      <div class="footer">
        <div class="status"><span class="dot" id="dot"></span><span id="statusText">Connecting...</span></div>
        <div>Last sent: <code id="lastMsg">—</code></div>
      </div>
    </div>
  </div>

  <div class="toast" id="toast"></div>

  <div class="modal" id="shutdownModal">
    <div class="modal-content">
      <h2>⚠️ Confirm Shutdown</h2>
      <p>Are you sure you want to shutdown the Raspberry Pi? This will turn off the system.</p>
      <div class="modal-buttons">
        <button class="btn" id="btnCancelShutdown">Cancel</button>
        <button class="btn btn-danger" id="btnConfirmShutdown">Shutdown</button>
      </div>
    </div>
  </div>

<script>
  const rb = document.getElementById('rainbowBrightness');
  const rbv = document.getElementById('rbv');
  const cb = document.getElementById('colorBrightness');
  const cbv = document.getElementById('cbv');
  const btnOff = document.getElementById('btnOff');
  const btnRainbow = document.getElementById('btnRainbow');
  const btnColor = document.getElementById('btnColor');
  const colorHex = document.getElementById('colorHex');
  const fadeToggle = document.getElementById('fadeToggle');
  const dot = document.getElementById('dot');
  const statusText = document.getElementById('statusText');
  const lastMsg = document.getElementById('lastMsg');
  const toast = document.getElementById('toast');
  const btnShutdown = document.getElementById('btnShutdown');
  const shutdownModal = document.getElementById('shutdownModal');
  const btnCancelShutdown = document.getElementById('btnCancelShutdown');
  const btnConfirmShutdown = document.getElementById('btnConfirmShutdown');

  const clamp = (v, min, max) => Math.max(min, Math.min(max, v|0));

  function showToast(text) {
    toast.textContent = text;
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 1600);
  }

  async function send(payload) {
    try {
      const res = await fetch('/api/lightbase', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (!res.ok || data.error) {
        dot.classList.remove('ok'); dot.classList.add('err');
        statusText.textContent = data.error || ('HTTP ' + res.status);
        showToast('Error: ' + (data.error || res.statusText));
      } else {
        dot.classList.remove('err'); dot.classList.add('ok');
        statusText.textContent = 'Connected';
        lastMsg.textContent = data.sent || '';
        showToast('Sent: ' + (data.sent || ''));
      }
    } catch (e) {
      dot.classList.remove('ok'); dot.classList.add('err');
      statusText.textContent = 'Network error';
      showToast('Network error');
    }
  }

  async function shutdown() {
    try {
      const res = await fetch('/api/shutdown', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'}
      });
      const data = await res.json();
      if (res.ok && data.ok) {
        showToast('Shutting down Pi...');
      } else {
        showToast('Shutdown failed: ' + (data.error || 'Unknown error'));
      }
    } catch (e) {
      showToast('Network error during shutdown');
    }
  }

  rb.addEventListener('input', () => rbv.textContent = rb.value);
  cb.addEventListener('input', () => cbv.textContent = cb.value);

  btnOff.addEventListener('click', () => {
    send({ mode: 'off' });
  });

  btnRainbow.addEventListener('click', () => {
    const brightness = clamp(parseInt(rb.value, 10), 0, 100);
    send({ mode: 'rainbow', brightness });
  });

  btnColor.addEventListener('click', () => {
    const hex = (colorHex.value || '#000000').replace('#','').toUpperCase();
    const brightness = clamp(parseInt(cb.value, 10), 0, 100);
    const fade = fadeToggle.checked ? 1 : 0;
    send({ mode: 'hex', hex, brightness, fade });
  });

  btnShutdown.addEventListener('click', () => {
    shutdownModal.classList.add('show');
  });

  btnCancelShutdown.addEventListener('click', () => {
    shutdownModal.classList.remove('show');
  });

  btnConfirmShutdown.addEventListener('click', () => {
    shutdownModal.classList.remove('show');
    shutdown();
  });

  (function initStatus(){
    fetch('/api/lightbase', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ mode: 'ping' })
    }).then(r => r.json()).then(d => {
      if (d.ok) { dot.classList.add('ok'); statusText.textContent = 'Connected'; }
      else { dot.classList.add('err'); statusText.textContent = d.error || 'Disconnected'; }
    }).catch(() => { dot.classList.add('err'); statusText.textContent = 'Disconnected'; });
  })();
</script>
</body>
</html>
"""

class Index:
    def GET(self):
        web.header("Content-Type", "text/html; charset=utf-8")
        return PAGE_HTML

def validate_payload(data):
    if not isinstance(data, dict): return "Invalid JSON"
    mode = data.get("mode")
    if mode == "ping":
        return None
    if mode == "off":
        return None
    if mode == "rainbow":
        b = data.get("brightness")
        if b is None: return "Missing brightness"
        try:
            b = int(b)
        except Exception:
            return "Brightness must be integer"
        if not (0 <= b <= 100): return "Brightness out of range (0-100)"
        return None
    if mode == "hex":
        hexv = (data.get("hex") or "").strip()
        if hexv.startswith("#"): hexv = hexv[1:]
        if not re.fullmatch(r"[0-9A-Fa-f]{6}", hexv or ""):
            return "hex must be RRGGBB"
        try:
            b = int(data.get("brightness"))
            f = int(data.get("fade"))
        except Exception:
            return "brightness and fade must be integers"
        if not (0 <= b <= 100): return "Brightness out of range (0-100)"
        if f not in (0, 1): return "Fade must be 0 or 1"
        return None
    return "Unknown mode"

def build_message(data):
    mode = data.get("mode")
    if mode == "off":
        return "off"
    if mode == "rainbow":
        return f"rainbow {int(data['brightness'])}"
    if mode == "hex":
        hexv = (data.get("hex") or "").replace("#", "").upper()
        b = int(data["brightness"])
        f = int(data["fade"])
        return f"Hex({hexv}) Brightness({b}) Fade({f})"
    if mode == "ping":
        return None
    return None

class LightBaseAPI:
    def POST(self):
        web.header("Content-Type", "application/json; charset=utf-8")
        try:
            raw = web.data()
            data = json.loads(raw.decode("utf-8") if isinstance(raw, (bytes, bytearray)) else raw)
        except Exception:
            return json.dumps({"ok": False, "error": "Invalid JSON"})
        err = validate_payload(data)
        if err:
            if data.get("mode") == "ping":
                return json.dumps({"ok": bool(mqtt_connected), "error": None if mqtt_connected else (mqtt_last_error or "MQTT not connected")})
            return json.dumps({"ok": False, "error": err})

        msg = build_message(data)
        if msg is None and data.get("mode") == "ping":
            return json.dumps({"ok": bool(mqtt_connected)})
        try:
            pub_info = publish_lightbase(msg)
            return json.dumps({"ok": True, "mid": pub_info.get("mid"), "sent": msg})
        except Exception as e:
            return json.dumps({"ok": False, "error": str(e)})

class ShutdownAPI:
    def POST(self):
        web.header("Content-Type", "application/json; charset=utf-8")
        try:
            print("[SHUTDOWN] Executing sudo poweroff...")
            os.system("sudo poweroff")
            return json.dumps({"ok": True, "message": "Shutdown initiated"})
        except Exception as e:
            return json.dumps({"ok": False, "error": str(e)})

if __name__ == "__main__":
    app = web.application(urls, globals())
    if web.config.get('_session') is None:
        web.config.debug = False
    app.run()