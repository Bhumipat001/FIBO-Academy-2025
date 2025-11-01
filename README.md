__The Desktop Friend Robot (Companian Robot)__
## Project CatLover
The robot friend who follows and interacts with a cute emotion. 

![Front View of the Robot](https://github.com/Bhumipat001/FIBO-Academy-2025/blob/main/img/Front%20Look%20of%20Robot.jpg)

Right now, the project is the prototype simulate some of the features that could have in the robot.   

## What does the program do?
Program is to sense the human and interact by base on conditions.

The file contains 2 devices program:
- ESP32 (WROOM)
- Raspberry Pi (4 Model B)

ESP32 is used for low level support and hub for sensors.
Including:
- Touch (Build-in Capacitive touch of ESP32)
- Vibrator Motor (PWM)
- Light Strip (WS2812B)
- Radar (24GHz mmWave Radar via UART--Serial2)
- Servo 

Raspberry Pi is used for high level support.
Including :
- Image processing (Object Detection)
- Display (ILI9341V via SPI)
- Sound (Rn, code supports only output)
- Motion Expression

![Components of the Robot](https://github.com/Bhumipat001/FIBO-Academy-2025/blob/main/img/Components%20Overview.png)

__Components__

ESP32:
| Device | Connection |
| -------- | -------- |
| Servo | PWM: 4, 5, 16, 17, 18, 19, 21, 22 |
| Touch (Wire or Thin Metal Sheet) | GPIO: 12, 13, 14, 27, 32, 33|
| Light Strip | NZR: 0, 23 |
| Radar | UART: Serial2 |
| Vibrator (Signal) | PWM: 2 |
| Raspberry Pi | UART: Serial0 |

Raspberry Pi:
| Device | Connection |
| -------- | -------- |
| Pi Camera | SCI (Ribbon Cable) |
| Display | SPI: 8(CS), 9(MISO), 10(MOSI), 11(SCK), 24(RS), 25(RST) |
| ESP32 | UART: Serial |
| Speaker (Signal) | Aux Jack |

## Design
The design is to mimic cat like but with creativity into it with CRT diplay head and hybrid with human look.

![Design of the Robot](https://github.com/Bhumipat001/FIBO-Academy-2025/blob/main/img/Design%20of%20the%20Robot.png)