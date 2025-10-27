#include "haptic.h"
#include <math.h>

static const int HAPTIC_LEDC_CHANNEL = 15;
static int s_hapticPin = 2;
static uint8_t s_resolutionBits = 8;
static uint32_t s_maxDuty = 255;
static volatile bool s_enabled = false;
static bool s_inited = false;
static uint32_t s_startMs = 0;

void initHaptic(int pin, int freqHz, uint8_t resolutionBits) {
  s_hapticPin = pin;
  s_resolutionBits = resolutionBits;
  s_maxDuty = (1UL << s_resolutionBits) - 1;

  ledcSetup(HAPTIC_LEDC_CHANNEL, freqHz, s_resolutionBits);
  ledcAttachPin(s_hapticPin, HAPTIC_LEDC_CHANNEL);
  ledcWrite(HAPTIC_LEDC_CHANNEL, 0);

  s_startMs = millis();
  s_inited = true;
}

void setHapticEnabled(bool on) {
  s_enabled = on;
  if (!s_inited) return;
  if (!on) {
    ledcWrite(HAPTIC_LEDC_CHANNEL, 0);
  } else {
    s_startMs = millis();
  }
}

bool isHapticEnabled() { return s_enabled; }
void updateHaptic() {
  if (!s_inited) return;

  if (!s_enabled) {
    ledcWrite(HAPTIC_LEDC_CHANNEL, 0);
    return;
  }

  uint32_t now = millis();
  uint32_t t = now - s_startMs;
  if (t >= BREATH_PERIOD_MS) {
    s_startMs = now - (t % BREATH_PERIOD_MS);
    t = now - s_startMs;
  }

  float phase = (float)t / (float)BREATH_PERIOD_MS;
  float x = 0.5f * (1.0f - cosf(2.0f * (float)M_PI * phase));

  float y = x * BREATH_STRENGTH;
  if (y < DUTY_DEADZONE) y = 0.0f;

  uint32_t duty = (uint32_t)(y * (float)s_maxDuty);
  if (duty > s_maxDuty) duty = s_maxDuty;
  ledcWrite(HAPTIC_LEDC_CHANNEL, duty);
}