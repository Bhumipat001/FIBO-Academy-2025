__The Desktop Friend Robot (Companian Robot)__
## Project CatLover
The robot friend who follows and interacts with a cute emotion. 

![Front View of the Robot](https://github.com/Bhumipat001/FIBO-Academy-2025/blob/main/img/Front%20Look%20of%20Robot.jpg)

Right now, the project is the prototype simulate some of the features that could have in the robot.   

## What does the program do?
Program is to __sense the human and interact by base on conditions__.

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
The design is to __mimic cat like but with creativity__ into it with CRT diplay head and hybrid with human look.

![Design of the Robot](https://github.com/Bhumipat001/FIBO-Academy-2025/blob/main/img/Design%20of%20the%20Robot.png)

__3D Design__(CAD): 
- [STEP Assembly](https://github.com/Bhumipat001/FIBO-Academy-2025/tree/main/CAD/STEP)
- [STL Files](https://github.com/Bhumipat001/FIBO-Academy-2025/tree/main/CAD/STL)

Note: The design is made to __manufacture by 3D Printer__(FDM Printer)

__Materials__:
- Sensors
    - `1` 24GHz mmWave Radar(Waveshare)
    - `A little bit` Thin Metalic(Aluminum Tape)
- `8` Servos
- Compute Modules
    - `1` ESP32 WROOM
    - `1` Raspberry Pi 4 Model B
- `1` Speaker (Support Size: 10 mm and 17 mm) and Amplifier
- `1` Pi Camera with Fish Eye Lense(130 Degree)
- `2` Light Strip with WS2812B
- `1` 3.2" TFT Screen
- `1` Vibrator Motor
- `Some` Wires
- `1` Power Supply, Switch, Connector and others

## Program Summery
We use local __MQTT__ broker(In our case we use Moquito) for communication inside the Raspberry Pi and ESP32(via Middle program). 

Here is the simple algorithm inside the program that running these boards.

![Simplified Algorithm of Raspberry Pi](https://github.com/Bhumipat001/FIBO-Academy-2025/blob/main/img/Algorithm%20inside%20Raspberry%20Pi.png)

![Simplified Algorithm of ESP32](https://github.com/Bhumipat001/FIBO-Academy-2025/blob/main/img/Algorithm%20inside%20ESP32.png)


### Tracking Program
![Algorithm of the Tracking Program](https://github.com/Bhumipat001/FIBO-Academy-2025/blob/main/img/Following%20Test.png)

The repositorie provides object detection model optimized from YOLOv8n. The program goal is to move the focus object to the center of the setpoint(middle of the screen).

### Radar Program
![Algorithm of the Radar Program](https://github.com/Bhumipat001/FIBO-Academy-2025/blob/main/img/Radar%20Test.png)

Note: 
The algorithm could be improve in many ways. This is the imprement to test how useful the sensor could help in the robot.

This imprementation is the test of using radar for sensing the hand in front of the face without touching the screen itself. The radar is using doppler effect to detect but the size and limitation the sensor could detect moving moving object far more better but that means if the sensor moving could cause the reading to be false or include the noise in the reading data.

More detail: [Link](https://github.com/Bhumipat001/FIBO-Academy-2025/blob/main/Present%20Slide.pdf)