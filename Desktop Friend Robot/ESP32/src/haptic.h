#pragma once
#include <Arduino.h>

static const uint32_t BREATH_PERIOD_MS = 5000;
static const float BREATH_STRENGTH = 0.80f;
static const float DUTY_DEADZONE = 0.06f;

void initHaptic(int pin = 2, int freqHz = 300, uint8_t resolutionBits = 8);
void setHapticEnabled(bool on);
bool isHapticEnabled();
void updateHaptic();