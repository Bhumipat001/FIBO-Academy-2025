#include <Arduino.h>
#include <math.h>
#include "follow.h"
#include "servo.h"

static float panPos = 90.0f;
static float panTarget = 90.0f;

static float headPos = 100.0f;
static float headTarget = 100.0f;

static const float STEP_DEG = 1.0f;
static unsigned long lastMovementTime = 0;
static bool servosAttached = false;
static const unsigned long DETACH_DELAY = 1000;

void parsePanCommand(String s) {
  s.trim();
  if (s.length() > 0) {
    panTarget = constrain(s.toFloat(), (float)Body_MIN, (float)Body_MAX);
  }
}

void parseHeadCommand(String s) {
  s.trim();
  if (s.length() > 0) {
    headTarget = constrain(s.toFloat(), (float)Head_MIN, (float)Head_MAX);
  }
}

void updateTracking() {
  bool bodyNeedsMove = fabs(panTarget - panPos) > 0.01f;
  bool headNeedsMove = fabs(headTarget - headPos) > 0.01f;

  if (bodyNeedsMove || headNeedsMove) {
    if (!servosAttached) {
      attachAllServos();
      servosAttached = true;
    }

    if (bodyNeedsMove) {
      float diff = panTarget - panPos;
      float step = min(STEP_DEG, fabs(diff));
      panPos += (diff > 0) ? step : -step;
      setBodyAngle((int)roundf(panPos));
    }

    if (headNeedsMove) {
      float diff = headTarget - headPos;
      float step = min(STEP_DEG, fabs(diff));
      headPos += (diff > 0) ? step : -step;
      setHeadAngle((int)roundf(headPos));
    }

    lastMovementTime = millis();
  } else {
    if (servosAttached && (millis() - lastMovementTime >= DETACH_DELAY)) {
      detachAllServos();
      servosAttached = false;
    }
  }
}

void initPan() {
  attachAllServos();
  setBodyAngle((int)roundf(panPos));
  setHeadAngle((int)roundf(headPos));
  lastMovementTime = millis();
  servosAttached = true;
}