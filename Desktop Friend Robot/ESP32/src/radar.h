#ifndef RADAR_H
#define RADAR_H
#include <Arduino.h>

const int RADAR_RX_PIN = 25;
const int RADAR_TX_PIN = 26;

void sendHexData(String hexString);
void readSerialData();
int parseRange(String data);
void taskRadar(void *pvParameters);
void initRadar();

#endif