#ifndef LIGHT_H
#define LIGHT_H

#include <stdint.h>
#include <Arduino.h>
#include <Adafruit_NeoPixel.h>

#define LED_PIN     23
#define LED_COUNT   16
#define LED_BASE_PIN     0
#define LED_BASE_COUNT   40

void initLight(uint8_t defaultBrightness = 100);
void updateEffects();
void off();
void offBase();
void offAll();
void handleSerialCommand(String command);
void handleBaseSerialCommand(String command);

#endif