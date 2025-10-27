#include "radar.h"

static int lastRadarState = -1;
static bool firstCheckDone = false;

void sendHexData(String hexString) {
  int len = hexString.length();
  if (len % 2 != 0) return;
  byte hexBytes[64];
  int outLen = 0;
  for (int i = 0; i < len && outLen < (int)sizeof(hexBytes); i += 2) {
    hexBytes[outLen++] = strtoul(hexString.substring(i, i + 2).c_str(), NULL, 16);
  }
  Serial2.write(hexBytes, outLen);
  Serial.println("Sent hex command to sensor.");
}

int parseRange(String data) {
  if (data.startsWith("Range ")) {
    String rangeStr = data.substring(6);
    rangeStr.trim();
    return rangeStr.toInt();
  }
  return -1;
}

void readSerialData() {
  while (Serial2.available() > 0) {
    String incomingData = Serial2.readStringUntil('\n');
    incomingData.trim();

    if (incomingData.startsWith("Range ")) {
      int range = parseRange(incomingData);

      if (range >= 0) {
        int currentState = (range <= 10) ? 1 : 0;

        if (currentState != lastRadarState) {
          Serial.println("Radar: " + String(currentState));
          lastRadarState = currentState;
          firstCheckDone = true;
        }
      }
    }
  }
}

void taskRadar(void *pvParameters) {
  while (true) {
    readSerialData();

    if (!firstCheckDone && millis() > 3000) {
      if (lastRadarState == -1) {
        Serial.println("Radar: 0");
        lastRadarState = 0;
      }
      firstCheckDone = true;
    }

    vTaskDelay(pdMS_TO_TICKS(50));
  }
}

void initRadar() {
  Serial2.begin(115200, SERIAL_8N1, RADAR_RX_PIN, RADAR_TX_PIN);
  delay(500);

  String hex_to_send = "FDFCFBFA0800120000006400000004030201";
  sendHexData(hex_to_send);
}