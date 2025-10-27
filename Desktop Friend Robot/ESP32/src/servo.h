#ifndef POSE_H
#define POSE_H
#include <Arduino.h>

constexpr int Base_MIN = 0;
constexpr int Base_MAX = 180;
constexpr int Body_MIN = 40;
constexpr int Body_MAX = 150;
constexpr int ArmBase_MIN = 75;
constexpr int ArmBase_MAX = 115;
constexpr int R_Arm_MIN = 10;
constexpr int R_Arm_MAX = 70;
constexpr int L_Arm_MIN = 110;
constexpr int L_Arm_MAX = 170;
constexpr int Head_MIN = 70;
constexpr int Head_MAX = 130;
constexpr int R_Ear_MIN = 90;
constexpr int R_Ear_MAX = 130;
constexpr int L_Ear_MIN = 50;
constexpr int L_Ear_MAX = 90;

constexpr int Base_PIN = 4;
constexpr int Body_PIN = 16;
constexpr int ArmBase_PIN = 17;
constexpr int R_Arm_PIN = 5;
constexpr int L_Arm_PIN = 18;
constexpr int Head_PIN = 19;
constexpr int R_Ear_PIN = 21;
constexpr int L_Ear_PIN = 22;

void initServos();
void detachAllServos();
void attachAllServos();
void setBodyAngle(int angle);
void setHeadAngle(int angle);

bool executePose(const char* poseName);

#endif