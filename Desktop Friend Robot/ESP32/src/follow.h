#ifndef FOLLOW_H
#define FOLLOW_H

#include <Arduino.h>
#include "servo.h"

void parsePanCommand(String s);
void parseHeadCommand(String s);
void updateTracking();
void initPan();

#endif