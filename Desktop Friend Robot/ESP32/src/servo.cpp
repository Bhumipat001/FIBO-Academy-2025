#include <ESP32Servo.h>
#include <Arduino.h>
#include <string.h>
#include "servo.h"

// static Servo Base;
static Servo Body;
static Servo ArmBase;
static Servo R_Arm;
static Servo L_Arm;
static Servo Head;
static Servo R_Ear;
static Servo L_Ear;

static inline int clampAngle(int angle, int minA, int maxA) {
  if (angle < minA) return minA;
  if (angle > maxA) return maxA;
  return angle;
}

static inline void writeSafe(Servo &srv, int angle, int minA, int maxA) {
  srv.write(clampAngle(angle, minA, maxA));
}

#define servo(srv, angle) writeSafe(srv, angle, srv##_MIN, srv##_MAX)

void initServos() {
  // Base.attach(Base_PIN);
  Body.attach(Body_PIN);
  ArmBase.attach(ArmBase_PIN);
  R_Arm.attach(R_Arm_PIN);
  L_Arm.attach(L_Arm_PIN);
  Head.attach(Head_PIN);
  R_Ear.attach(R_Ear_PIN);
  L_Ear.attach(L_Ear_PIN);
}

void detachAllServos() {
  delay(1000);
  Body.detach();
  ArmBase.detach();
  R_Arm.detach();
  L_Arm.detach();
  Head.detach();
  R_Ear.detach();
  L_Ear.detach();
}

void attachAllServos() {
  Body.attach(Body_PIN);
  ArmBase.attach(ArmBase_PIN);
  R_Arm.attach(R_Arm_PIN);
  L_Arm.attach(L_Arm_PIN);
  Head.attach(Head_PIN);
  R_Ear.attach(R_Ear_PIN);
  L_Ear.attach(L_Ear_PIN);
}

void setBodyAngle(int angle) {
  servo(Body, angle);
}

void setHeadAngle(int angle) {
  servo(Head, angle);
}

typedef void (*PoseFunction)();

struct PoseEntry {
  const char* name;
  PoseFunction function;
};

#define ALL_POSES(P) \
  P(stretch) \
  P(ear) \
  P(clap) \
  P(no) \
  P(wave) \
  P(ear0) \
  P(ear1)

#define DECLARE_POSE(name) static void name();
#define REGISTER_POSE(name) {#name, name},

ALL_POSES(DECLARE_POSE)

static const PoseEntry poses[] = {
  ALL_POSES(REGISTER_POSE)
};

static const int numPoses = sizeof(poses) / sizeof(poses[0]);

static void stretch() {
  attachAllServos();
  // servo(Base, 30);
  servo(Body, 85);
  servo(ArmBase, 75);
  //servo(R_Arm, 70);
  //servo(L_Arm, 110);
  servo(Head, 100);
  servo(R_Ear, 130);
  servo(L_Ear, 50);
  delay(2000);
  //servo(ArmBase, 115);
  servo(R_Arm, 10);
  servo(L_Arm, 170);
  servo(R_Ear, 90);
  servo(L_Ear, 90);
  detachAllServos();
}

static void ear() {
  attachAllServos();
  servo(R_Ear, 130);
  servo(L_Ear, 50);
  delay(100);
  servo(R_Ear, 90);
  servo(L_Ear, 90);
  detachAllServos();
}

static void ear0() {
  attachAllServos();
  servo(R_Ear, 90);
  servo(L_Ear, 90);
  delay(300);
  detachAllServos();
}

static void ear1() {
  attachAllServos();
  servo(R_Ear, 130);
  servo(L_Ear, 50);
  delay(300);
  detachAllServos();
}

static void clap() {
  attachAllServos();
  servo(ArmBase, 90);
  servo(R_Arm, 90);
  servo(L_Arm, 90);
  delay(100);
  servo(ArmBase, 110);
  delay(100);
  servo(ArmBase, 75);
  delay(100);
  servo(ArmBase, 110);
  delay(100);
  servo(ArmBase, 75);
  delay(100);
  servo(ArmBase, 110);
  delay(100);
  servo(ArmBase, 90);
  servo(R_Arm, 10);
  servo(L_Arm, 170);
  detachAllServos();
}

static void no(){
  attachAllServos();
  servo(Head, 100);
  servo(Head, 80);
  delay(200);
  servo(Head, 120);
  delay(200);
  servo(Head, 80);
  delay(200);
  servo(Head, 120);
  delay(200);
  servo(Head, 80);
  delay(200);
  servo(Head, 120);
  servo(Head, 100);
  detachAllServos();
}

static void wave(){
  attachAllServos();
  servo(ArmBase, 90);
  servo(R_Arm, 90);
  delay(200);
  servo(R_Arm, 60);
  delay(100);
  servo(R_Arm, 90);
  delay(100);
  servo(R_Arm, 60);
  delay(100);
  servo(R_Arm, 90);
  delay(100);
  servo(R_Arm, 60);
  delay(100);
  servo(ArmBase, 90);
  servo(R_Arm, 10);
  detachAllServos();
}

bool executePose(const char* poseName) {
  for (int i = 0; i < numPoses; i++) {
    if (strcmp(poses[i].name, poseName) == 0) {
      poses[i].function();
      return true;
    }
  }
  return false;
}