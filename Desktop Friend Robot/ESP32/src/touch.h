#ifndef TOUCH_H                                                
#define TOUCH_H
#include <Arduino.h>

const int L_BODY_PIN = 13;
const int R_BODY_PIN = 12;
const int F_BODY_PIN = 14;
const int B_BODY_PIN = 27;
const int L_HEAD_PIN = 33;
const int R_HEAD_PIN = 32;

const int CALIBRATION_SAMPLES = 100;

const float L_Body_Threshold = 0.01;
const float R_Body_Threshold = 0.01;
const float F_Body_Threshold = 0.01;
const float B_Body_Threshold = 0.01;
const float L_Head_Threshold = 0.80;
const float R_Head_Threshold = 0.01;

struct TouchStates {
  bool L_Body;
  bool R_Body;
  bool F_Body;
  bool B_Body;
  bool L_Head;
  bool R_Head;
};

void calibrateAllSensors();
TouchStates getAllTouchStates();
void taskTouch(void *pvParameters);

#endif