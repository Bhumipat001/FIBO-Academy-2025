#include "light.h"

static Adafruit_NeoPixel strip(LED_COUNT, LED_PIN, NEO_GRB + NEO_KHZ800);
static Adafruit_NeoPixel stripBase(LED_BASE_COUNT, LED_BASE_PIN, NEO_GRB + NEO_KHZ800);
#define BLINK_DELAY 300

static unsigned long lastFadeTime = 0;
static bool fadeEnabled = false;
static uint8_t fadeValue = 0;
static uint8_t fadeTarget = 0;
static uint8_t targetR = 0, targetG = 0, targetB = 0;
static uint8_t currentR = 0, currentG = 0, currentB = 0;
static uint8_t brightness = 100;
static bool rainbowEnabled = false;
static uint16_t rainbowState = 0;
static uint8_t rainbowBrightness = 100;
static bool colorTransitionEnabled = false;
static bool breathingEnabled = false;
static uint8_t breathingMax = 100;
static const unsigned long FADE_DURATION_MS = 2000;

static unsigned long lastFadeTimeBase = 0;
static bool fadeEnabledBase = false;
static uint8_t fadeValueBase = 0;
static uint8_t fadeTargetBase = 0;
static uint8_t targetRBase = 0, targetGBase = 0, targetBBase = 0;
static uint8_t currentRBase = 0, currentGBase = 0, currentBBase = 0;
static uint8_t brightnessBase = 100;
static bool rainbowEnabledBase = false;
static uint16_t rainbowStateBase = 0;
static uint8_t rainbowBrightnessBase = 100;
static bool colorTransitionEnabledBase = false;
static bool breathingEnabledBase = false;
static uint8_t breathingMaxBase = 100;

static uint32_t Wheel(byte WheelPos) {
  WheelPos = 255 - WheelPos;
  if (WheelPos < 85) {
    return strip.Color(255 - WheelPos * 3, 0, WheelPos * 3);
  }
  if (WheelPos < 170) {
    WheelPos -= 85;
    return strip.Color(0, WheelPos * 3, 255 - WheelPos * 3);
  }
  WheelPos -= 170;
  return strip.Color(WheelPos * 3, 255 - WheelPos * 3, 0);
}

static void setAllPixels(uint8_t r, uint8_t g, uint8_t b, uint8_t brPercent) {
  uint8_t br = constrain(brPercent, 0, 100);
  r = (r * br) / 100;
  g = (g * br) / 100;
  b = (b * br) / 100;
  for (uint16_t i = 0; i < strip.numPixels(); i++) {
    strip.setPixelColor(i, strip.Color(r, g, b));
  }
  strip.show();
}

void initLight(uint8_t defaultBrightness) {
  strip.begin();
  strip.show();
  strip.setBrightness(128);
  brightness = constrain(defaultBrightness, 0, 100);
  rainbowBrightness = brightness;
  fadeEnabled = true;
  fadeValue = 0;
  fadeTarget = brightness;
  lastFadeTime = millis();
  rainbowEnabled = true;
  rainbowState = 0;
  colorTransitionEnabled = false;
  breathingEnabled = false;
  targetR = currentR = 0;
  targetG = currentG = 0;
  targetB = currentB = 0;

  stripBase.begin();
  stripBase.show();
  stripBase.setBrightness(128);
  brightnessBase = constrain(defaultBrightness, 0, 100);
  rainbowBrightnessBase = brightnessBase;
  fadeEnabledBase = true;
  fadeValueBase = 0;
  fadeTargetBase = brightnessBase;
  lastFadeTimeBase = millis();
  rainbowEnabledBase = true;
  rainbowStateBase = 0;
  colorTransitionEnabledBase = false;
  breathingEnabledBase = false;
  targetRBase = currentRBase = 0;
  targetGBase = currentGBase = 0;
  targetBBase = currentBBase = 0;
}

void updateEffects() {
  if (fadeEnabled) {
    unsigned long now = millis();
    unsigned long elapsed = now - lastFadeTime;

    if (elapsed > 0) {
      int distance = abs((int)fadeTarget - (int)fadeValue);
      if (distance > 0) {
        float range = breathingEnabled ? (float)breathingMax : 100.0f;
        float stepsPerMs = range / (float)FADE_DURATION_MS;
        float stepsToMove = elapsed * stepsPerMs;
        if (stepsToMove >= 1.0f) {
          lastFadeTime = now;
          int steps = (int)stepsToMove;
          steps = min(steps, distance);
          if (fadeValue < fadeTarget) {
            fadeValue += steps;
            if (fadeValue > fadeTarget) fadeValue = fadeTarget;
          } else {
            fadeValue -= steps;
            if (fadeValue < fadeTarget) fadeValue = fadeTarget;
          }
        }
      }
      if (fadeValue == fadeTarget) {
        if (breathingEnabled) {
          fadeTarget = (fadeTarget == 0) ? breathingMax : 0;
        } else {
          brightness = fadeTarget;
          rainbowBrightness = fadeTarget;
          fadeEnabled = false;
        }
      }
    }
  }

  if (colorTransitionEnabled && !rainbowEnabled) {
    bool transitioning = false;
    if (currentR < targetR) { currentR++; transitioning = true; }
    else if (currentR > targetR) { currentR--; transitioning = true; }

    if (currentG < targetG) { currentG++; transitioning = true; }
    else if (currentG > targetG) { currentG--; transitioning = true; }

    if (currentB < targetB) { currentB++; transitioning = true; }
    else if (currentB > targetB) { currentB--; transitioning = true; }

    if (!transitioning) {
      colorTransitionEnabled = false;
    }
  }

  if (rainbowEnabled) {
    uint8_t effectiveBrightness = fadeEnabled ? fadeValue : rainbowBrightness;
    for (uint16_t i = 0; i < strip.numPixels(); i++) {
      uint32_t color = Wheel(((i * 256 / strip.numPixels()) + rainbowState) & 255);
      uint8_t r = (color >> 16) & 0xFF;
      uint8_t g = (color >> 8) & 0xFF;
      uint8_t b = color & 0xFF;
      r = (r * effectiveBrightness) / 100;
      g = (g * effectiveBrightness) / 100;
      b = (b * effectiveBrightness) / 100;
      strip.setPixelColor(i, strip.Color(r, g, b));
    }
    strip.show();
    static bool rainbowTick = false;
    rainbowTick = !rainbowTick;
    if (rainbowTick) {
      rainbowState = (rainbowState + 1) % 256;
    }
  } else {
    uint8_t effectiveBrightness = fadeEnabled ? fadeValue : brightness;
    setAllPixels(currentR, currentG, currentB, effectiveBrightness);
  }

  if (fadeEnabledBase) {
    unsigned long now = millis();
    unsigned long elapsed = now - lastFadeTimeBase;

    if (elapsed > 0) {
      int distance = abs((int)fadeTargetBase - (int)fadeValueBase);
      if (distance > 0) {
        float range = breathingEnabledBase ? (float)breathingMaxBase : 100.0f;
        float stepsPerMs = range / (float)FADE_DURATION_MS;
        float stepsToMove = elapsed * stepsPerMs;
        if (stepsToMove >= 1.0f) {
          lastFadeTimeBase = now;
          int steps = (int)stepsToMove;
          steps = min(steps, distance);
          if (fadeValueBase < fadeTargetBase) {
            fadeValueBase += steps;
            if (fadeValueBase > fadeTargetBase) fadeValueBase = fadeTargetBase;
          } else {
            fadeValueBase -= steps;
            if (fadeValueBase < fadeTargetBase) fadeValueBase = fadeTargetBase;
          }
        }
      }
      if (fadeValueBase == fadeTargetBase) {
        if (breathingEnabledBase) {
          fadeTargetBase = (fadeTargetBase == 0) ? breathingMaxBase : 0;
        } else {
          brightnessBase = fadeTargetBase;
          rainbowBrightnessBase = fadeTargetBase;
          fadeEnabledBase = false;
        }
      }
    }
  }

  if (colorTransitionEnabledBase && !rainbowEnabledBase) {
    bool transitioning = false;
    if (currentRBase < targetRBase) { currentRBase++; transitioning = true; }
    else if (currentRBase > targetRBase) { currentRBase--; transitioning = true; }

    if (currentGBase < targetGBase) { currentGBase++; transitioning = true; }
    else if (currentGBase > targetGBase) { currentGBase--; transitioning = true; }

    if (currentBBase < targetBBase) { currentBBase++; transitioning = true; }
    else if (currentBBase > targetBBase) { currentBBase--; transitioning = true; }

    if (!transitioning) {
      colorTransitionEnabledBase = false;
    }
  }

  if (rainbowEnabledBase) {
    uint8_t effectiveBrightness = fadeEnabledBase ? fadeValueBase : rainbowBrightnessBase;
    for (uint16_t i = 0; i < stripBase.numPixels(); i++) {
      uint32_t color = Wheel(((i * 256 / stripBase.numPixels()) + rainbowStateBase) & 255);
      uint8_t r = (color >> 16) & 0xFF;
      uint8_t g = (color >> 8) & 0xFF;
      uint8_t b = color & 0xFF;
      r = (r * effectiveBrightness) / 100;
      g = (g * effectiveBrightness) / 100;
      b = (b * effectiveBrightness) / 100;
      stripBase.setPixelColor(i, stripBase.Color(r, g, b));
    }
    stripBase.show();
    static bool rainbowTickBase = false;
    rainbowTickBase = !rainbowTickBase;
    if (rainbowTickBase) {
      rainbowStateBase = (rainbowStateBase + 1) % 256;
    }
  } else {
    uint8_t effectiveBrightness = fadeEnabledBase ? fadeValueBase : brightnessBase;
    uint8_t br = constrain(effectiveBrightness, 0, 100);
    uint8_t r = (currentRBase * br) / 100;
    uint8_t g = (currentGBase * br) / 100;
    uint8_t b = (currentBBase * br) / 100;
    for (uint16_t i = 0; i < stripBase.numPixels(); i++) {
      stripBase.setPixelColor(i, stripBase.Color(r, g, b));
    }
    stripBase.show();
  }
}

void off() {
  breathingEnabled = false;
  fadeEnabled = true;
  uint8_t currentEffective = rainbowEnabled ? rainbowBrightness : brightness;
  fadeValue = currentEffective;
  fadeTarget = 0;
  lastFadeTime = millis();
}

void offBase() {
  breathingEnabledBase = false;
  fadeEnabledBase = true;
  uint8_t currentEffective = rainbowEnabledBase ? rainbowBrightnessBase : brightnessBase;
  fadeValueBase = currentEffective;
  fadeTargetBase = 0;
  lastFadeTimeBase = millis();
}

void offAll() {
  off();
  offBase();
}

static bool parseHexCommand(String command, uint8_t &r, uint8_t &g, uint8_t &b, uint8_t &bright, bool &fade) {
  int hexIdx = command.indexOf("Hex(");
  int brightIdx = command.indexOf("Brightness(");
  int fadeIdx = command.indexOf("Fade(");
  if (hexIdx == -1 || brightIdx == -1 || fadeIdx == -1) return false;
  int hexEnd = command.indexOf(')', hexIdx);
  int brightEnd = command.indexOf(')', brightIdx);
  int fadeEnd = command.indexOf(')', fadeIdx);
  if (hexEnd == -1 || brightEnd == -1 || fadeEnd == -1) return false;
  String hexStr = command.substring(hexIdx + 4, hexEnd);
  if (hexStr.length() != 6) return false;
  r = strtol(hexStr.substring(0,2).c_str(), nullptr, 16);
  g = strtol(hexStr.substring(2,4).c_str(), nullptr, 16);
  b = strtol(hexStr.substring(4,6).c_str(), nullptr, 16);
  bright = command.substring(brightIdx + 11, brightEnd).toInt();
  fade = command.substring(fadeIdx + 5, fadeEnd).toInt() == 1;
  return true;
}

void handleSerialCommand(String command) {
  if (command == "off") {
    off();
    return;
  }
  if (command.startsWith("rainbow")) {
    command.trim();
    int spaceIdx = command.indexOf(' ');
    int targetBrightness;
    if (spaceIdx != -1) {
      String brightnessStr = command.substring(spaceIdx + 1);
      brightnessStr.trim();
      int bright = brightnessStr.toInt();
      targetBrightness = constrain(bright, 0, 100);
    } else {
      targetBrightness = 100;
    }

    uint8_t currentEffectiveBrightness = fadeEnabled ? fadeValue : (rainbowEnabled ? rainbowBrightness : brightness);

    if (!rainbowEnabled) {
      fadeEnabled = true;
      fadeValue = currentEffectiveBrightness;
      fadeTarget = 0;
      lastFadeTime = millis();
      rainbowBrightness = targetBrightness;
      rainbowEnabled = true;
      rainbowState = 0;
      breathingEnabled = false;
      fadeTarget = rainbowBrightness;
      lastFadeTime = millis();
    } else {
      rainbowEnabled = true;
      rainbowState = 0;
      rainbowBrightness = targetBrightness;
      breathingEnabled = false;
      fadeEnabled = true;
      fadeValue = currentEffectiveBrightness;
      fadeTarget = rainbowBrightness;
      lastFadeTime = millis();
    }
    return;
  }
  uint8_t r, g, b, bright;
  bool fade;
  if (parseHexCommand(command, r, g, b, bright, fade)) {
    uint8_t currentEffectiveBrightness = fadeEnabled ? fadeValue : (rainbowEnabled ? rainbowBrightness : brightness);
    if (rainbowEnabled) {
      uint32_t lastColor = Wheel(((0 * 256 / strip.numPixels()) + rainbowState) & 255);
      currentR = (lastColor >> 16) & 0xFF;
      currentG = (lastColor >> 8) & 0xFF;
      currentB = lastColor & 0xFF;
    }

    targetR = r;
    targetG = g;
    targetB = b;
    brightness = constrain(bright, 0, 100);
    rainbowEnabled = false;
    colorTransitionEnabled = true;

    if (fade) {
      breathingEnabled = true;
      breathingMax = brightness;
      fadeEnabled = true;
      fadeValue = currentEffectiveBrightness;
      fadeTarget = (fadeValue < breathingMax / 2) ? breathingMax : 0;
      lastFadeTime = millis();
    } else {
      breathingEnabled = false;
      fadeEnabled = true;
      fadeValue = currentEffectiveBrightness;
      fadeTarget = brightness;
      lastFadeTime = millis();
    }
  }
}

void handleBaseSerialCommand(String command) {
  if (command == "off") {
    offBase();
    return;
  }
  if (command.startsWith("rainbow")) {
    command.trim();
    int spaceIdx = command.indexOf(' ');
    int targetBrightness;
    if (spaceIdx != -1) {
      String brightnessStr = command.substring(spaceIdx + 1);
      brightnessStr.trim();
      int bright = brightnessStr.toInt();
      targetBrightness = constrain(bright, 0, 100);
    } else {
      targetBrightness = 100;
    }

    uint8_t currentEffectiveBrightness = fadeEnabledBase ? fadeValueBase : (rainbowEnabledBase ? rainbowBrightnessBase : brightnessBase);

    if (!rainbowEnabledBase) {
      fadeEnabledBase = true;
      fadeValueBase = currentEffectiveBrightness;
      fadeTargetBase = 0;
      lastFadeTimeBase = millis();
      rainbowBrightnessBase = targetBrightness;
      rainbowEnabledBase = true;
      rainbowStateBase = 0;
      breathingEnabledBase = false;
      fadeTargetBase = rainbowBrightnessBase;
      lastFadeTimeBase = millis();
    } else {
      rainbowEnabledBase = true;
      rainbowStateBase = 0;
      rainbowBrightnessBase = targetBrightness;
      breathingEnabledBase = false;
      fadeEnabledBase = true;
      fadeValueBase = currentEffectiveBrightness;
      fadeTargetBase = rainbowBrightnessBase;
      lastFadeTimeBase = millis();
    }
    return;
  }
  uint8_t r, g, b, bright;
  bool fade;
  if (parseHexCommand(command, r, g, b, bright, fade)) {
    uint8_t currentEffectiveBrightness = fadeEnabledBase ? fadeValueBase : (rainbowEnabledBase ? rainbowBrightnessBase : brightnessBase);
    if (rainbowEnabledBase) {
      uint32_t lastColor = Wheel(((0 * 256 / stripBase.numPixels()) + rainbowStateBase) & 255);
      currentRBase = (lastColor >> 16) & 0xFF;
      currentGBase = (lastColor >> 8) & 0xFF;
      currentBBase = lastColor & 0xFF;
    }

    targetRBase = r;
    targetGBase = g;
    targetBBase = b;
    brightnessBase = constrain(bright, 0, 100);
    rainbowEnabledBase = false;
    colorTransitionEnabledBase = true;

    if (fade) {
      breathingEnabledBase = true;
      breathingMaxBase = brightnessBase;
      fadeEnabledBase = true;
      fadeValueBase = currentEffectiveBrightness;
      fadeTargetBase = (fadeValueBase < breathingMaxBase / 2) ? breathingMaxBase : 0;
      lastFadeTimeBase = millis();
    } else {
      breathingEnabledBase = false;
      fadeEnabledBase = true;
      fadeValueBase = currentEffectiveBrightness;
      fadeTargetBase = brightnessBase;
      lastFadeTimeBase = millis();
    }
  }
}