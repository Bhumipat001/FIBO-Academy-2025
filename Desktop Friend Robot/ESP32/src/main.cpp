#include <Arduino.h>
#include <ESP32Servo.h>
#include <Adafruit_NeoPixel.h>
#include "servo.h"
#include "light.h"
#include "touch.h"
#include "radar.h"
#include "follow.h"
#include "haptic.h"

const unsigned long LOOP_MS = 25;
const int BOOT_PIN = 15;
unsigned long lastCheckTime = 0;
bool bootSequenceComplete = false;
unsigned long bootCommandTime = 0;

TaskHandle_t TaskTouch;
TaskHandle_t TaskServo;
TaskHandle_t TaskLight;
TaskHandle_t TaskRadar;

void taskLight(void *pvParameters) {
  while (true) {
    updateEffects();
    updateHaptic();
    vTaskDelay(pdMS_TO_TICKS(20));
  }
}

void taskServo(void *pvParameters) {
  while (true) {
    static int lastBootPinState = LOW;
    int bootPinState = digitalRead(BOOT_PIN);
    if (bootPinState == HIGH && lastBootPinState == LOW && !bootSequenceComplete) {
      Serial.println("Boot pin HIGH - triggering boot sequence");
      bootCommandTime = millis();
    }
    lastBootPinState = bootPinState;

    while (Serial.available() > 0) {
      String command = Serial.readStringUntil('\n');
      command.trim();

      if (command.startsWith("Servo: ")) {
        String pose = command.substring(7);
        Serial.print("Executing pose: ");
        Serial.println(pose);
        if (!executePose(pose.c_str())) {
          Serial.print("Unknown pose: ");
          Serial.println(pose);
        }
      } else if (command.startsWith("Light: ")) {
        handleSerialCommand(command.substring(7));
      } else if (command.startsWith("LightBase: ")) {
        handleBaseSerialCommand(command.substring(11));
      } else if (command.startsWith("Haptic: ")) {
        String arg = command.substring(8);
        arg.trim();
        if (arg == "1") {
          setHapticEnabled(true);
          Serial.println("Haptic enabled");
        } else {
          setHapticEnabled(false);
          Serial.println("Haptic disabled");
        }
      } else if (command.startsWith("Body: ")) {
        String arg = command.substring(6);
        parsePanCommand(arg);
      } else if (command.startsWith("Head: ")) {
        String arg = command.substring(6);
        parseHeadCommand(arg);
      }
    }

    if (!bootSequenceComplete && bootCommandTime != 0 && (millis() - bootCommandTime >= 1000)) {
      handleSerialCommand("Hex(B5B5B5) Brightness(100) Fade(0)");
      handleBaseSerialCommand("Hex(FFB126) Brightness(100) Fade(0)");
      vTaskDelay(pdMS_TO_TICKS(2000));
      executePose("stretch");
      bootSequenceComplete = true;
    } else if (!bootSequenceComplete && bootCommandTime == 0) {
      handleSerialCommand("off");
      handleBaseSerialCommand("off");
    }

    updateTracking();
    vTaskDelay(pdMS_TO_TICKS(LOOP_MS));
  }
}

void setup() {
  Serial.begin(115200);
  Serial.setTimeout(10);
  
  initRadar();
  initLight();
  initHaptic();

  initServos();
  initPan();
  pinMode(BOOT_PIN, INPUT_PULLDOWN);
  if (digitalRead(BOOT_PIN) == HIGH) {
    Serial.println("BOOT_PIN is HIGH at startup - scheduling boot sequence");
    bootCommandTime = millis();
  }

  xTaskCreatePinnedToCore(taskLight, "TaskLight", 4096, NULL, 1, &TaskLight, 0);
  delay(1000);
  calibrateAllSensors();

  xTaskCreatePinnedToCore(taskTouch, "TaskTouch", 4096, NULL, 1, &TaskTouch, 0);
  xTaskCreatePinnedToCore(taskRadar, "TaskRadar", 4096, NULL, 1, &TaskRadar, 0);
  xTaskCreatePinnedToCore(taskServo, "TaskServo", 4096, NULL, 1, &TaskServo, 1);
}

void loop() {
}