#include "touch.h"
#include <string.h>

static int L_Body_touchThreshold, L_Body_baselineValue;
static int R_Body_touchThreshold, R_Body_baselineValue;
static int F_Body_touchThreshold, F_Body_baselineValue;
static int B_Body_touchThreshold, B_Body_baselineValue;
static int L_Head_touchThreshold, L_Head_baselineValue;
static int R_Head_touchThreshold, R_Head_baselineValue;

static void calibrateTouchSensor(int pin, int &baseline, int &threshold, const char* sensorName) {
  long sum = 0;
  int maxVal = 0;
  int minVal = 100000;

  Serial.print("Calibrating ");
  Serial.print(sensorName);
  Serial.println(" sensor...");

  for (int i = 0; i < CALIBRATION_SAMPLES; i++) {
    int reading = touchRead(pin);
    sum += reading;
    maxVal = max(maxVal, reading);
    minVal = min(minVal, reading);
    delay(10);
  }
  baseline = sum / CALIBRATION_SAMPLES;

  if (strcmp(sensorName, "L_Body") == 0) threshold = baseline * L_Body_Threshold;
  else if (strcmp(sensorName, "R_Body") == 0) threshold = baseline * R_Body_Threshold;
  else if (strcmp(sensorName, "F_Body") == 0) threshold = baseline * F_Body_Threshold;
  else if (strcmp(sensorName, "B_Body") == 0) threshold = baseline * B_Body_Threshold;
  else if (strcmp(sensorName, "L_Head") == 0) threshold = baseline * L_Head_Threshold;
  else if (strcmp(sensorName, "R_Head") == 0) threshold = baseline * R_Head_Threshold;

  Serial.print(sensorName);
  Serial.println(" calibration complete!");
  Serial.print("Baseline value: ");
  Serial.println(baseline);
  Serial.print("Touch threshold: ");
  Serial.println(threshold);
}

static bool isTouched(int pin, int threshold) {
  int touchValue = touchRead(pin);
  return touchValue < threshold;
}

void calibrateAllSensors() {
  calibrateTouchSensor(L_BODY_PIN, L_Body_baselineValue, L_Body_touchThreshold, "L_Body");
  calibrateTouchSensor(R_BODY_PIN, R_Body_baselineValue, R_Body_touchThreshold, "R_Body");
  calibrateTouchSensor(F_BODY_PIN, F_Body_baselineValue, F_Body_touchThreshold, "F_Body");
  calibrateTouchSensor(B_BODY_PIN, B_Body_baselineValue, B_Body_touchThreshold, "B_Body");
  calibrateTouchSensor(L_HEAD_PIN, L_Head_baselineValue, L_Head_touchThreshold, "L_Head");
  calibrateTouchSensor(R_HEAD_PIN, R_Head_baselineValue, R_Head_touchThreshold, "R_Head");
}

TouchStates getAllTouchStates() {
  TouchStates states;
  states.L_Body = isTouched(L_BODY_PIN, L_Body_touchThreshold);
  states.R_Body = isTouched(R_BODY_PIN, R_Body_touchThreshold);
  states.F_Body = isTouched(F_BODY_PIN, F_Body_touchThreshold);
  states.B_Body = isTouched(B_BODY_PIN, B_Body_touchThreshold);
  states.L_Head = isTouched(L_HEAD_PIN, L_Head_touchThreshold);
  states.R_Head = isTouched(R_HEAD_PIN, R_Head_touchThreshold);
  return states;
}

void taskTouch(void *pvParameters) {
  static unsigned long lastRecalibrationTime = 0;
  static TouchStates lastTouchStates = {false, false, false, false, false, false};

  while (true) {
    if (millis() - lastRecalibrationTime >= 3600000) {
      calibrateAllSensors();
      lastRecalibrationTime = millis();
    }

    TouchStates currentTouchStates = getAllTouchStates();
    if (memcmp(&currentTouchStates, &lastTouchStates, sizeof(TouchStates)) != 0) {
      Serial.print("Touch: ");
      Serial.print("L_BODY=");
      Serial.print(currentTouchStates.L_Body ? "1" : "0");
      Serial.print(", R_BODY=");
      Serial.print(currentTouchStates.R_Body ? "1" : "0");
      Serial.print(", F_BODY=");
      Serial.print(currentTouchStates.F_Body ? "1" : "0");
      Serial.print(", B_BODY=");
      Serial.print(currentTouchStates.B_Body ? "1" : "0");
      Serial.print(", L_HEAD=");
      Serial.print(currentTouchStates.L_Head ? "1" : "0");
      Serial.print(", R_HEAD=");
      Serial.println(currentTouchStates.R_Head ? "1" : "0");
    }

    lastTouchStates = currentTouchStates;
    vTaskDelay(pdMS_TO_TICKS(100));
  }
}