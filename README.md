# The Desktop Friend Robot (Companion Robot)

## Project CatLover
A robotic friend that follows and interacts with humans, designed with a cute and emotional personality.

![Front View of the Robot](https://github.com/Bhumipat001/FIBO-Academy-2025/blob/main/img/Front%20Look%20of%20Robot.jpg)

This project is currently a prototype that simulates some of the features envisioned for the robot.

---

## What Does the Program Do?
The program is designed to **sense humans and interact with them based on specific conditions**.

### Devices Used
The project involves two main devices:
1. **ESP32 (WROOM)** - Handles low-level support and acts as a hub for sensors.
2. **Raspberry Pi (4 Model B)** - Provides high-level support for advanced features.

### ESP32 Features
- **Sensors**:
  - Capacitive Touch (built-in)
  - 24GHz mmWave Radar (via UART - Serial2)
- **Actuators**:
  - Vibrator Motor (PWM)
  - Light Strip (WS2812B)
  - Servo Motors

### Raspberry Pi Features
- **Image Processing**: Object detection
- **Display**: ILI9341V (via SPI)
- **Sound**: Audio output
- **Motion Expression**

![Components of the Robot](https://github.com/Bhumipat001/FIBO-Academy-2025/blob/main/img/Components%20Overview.png)

---

## Components

### ESP32 Connections
| Device                  | Connection                     |
|-------------------------|---------------------------------|
| Servo                  | PWM: 4, 5, 16, 17, 18, 19, 21, 22 |
| Touch (Wire/Metal Sheet)| GPIO: 12, 13, 14, 27, 32, 33   |
| Light Strip            | NZR: 0, 23                     |
| Radar                  | UART: Serial2                  |
| Vibrator (Signal)      | PWM: 2                         |
| Raspberry Pi           | UART: Serial0                  |

### Raspberry Pi Connections
| Device      | Connection                                   |
|-------------|---------------------------------------------|
| Pi Camera   | SCI (Ribbon Cable)                         |
| Display     | SPI: 8(CS), 9(MISO), 10(MOSI), 11(SCK), 24(RS), 25(RST) |
| ESP32       | UART: Serial                               |
| Speaker     | Aux Jack                                   |

---

## Design
The robot is designed to **mimic a cat-like appearance** with creative elements, including a CRT display head and a hybrid human-like look.

![Design of the Robot](https://github.com/Bhumipat001/FIBO-Academy-2025/blob/main/img/Design%20of%20the%20Robot.png)

### 3D Design (CAD)
- [STEP Assembly](https://github.com/Bhumipat001/FIBO-Academy-2025/tree/main/CAD/STEP)
- [STL Files](https://github.com/Bhumipat001/FIBO-Academy-2025/tree/main/CAD/STL)

**Note**: The design is optimized for **3D printing** (FDM printers).

---

## Materials
### Sensors
- `1` 24GHz mmWave Radar (Waveshare)
- `1` Pi Camera with Fish Eye Lens (130°)
- `A small amount` of thin metallic material (e.g., aluminum tape)

### Actuators
- `8` Servo Motors
- `2` Light Strips (WS2812B)
- `1` Vibrator Motor

### Compute Modules
- `1` ESP32 WROOM
- `1` Raspberry Pi 4 Model B

### Other Components
- `1` 3.2" TFT Screen
- `1` Speaker (10 mm or 17 mm) with Amplifier
- `Some` wires, power supply, switches, connectors, etc.

---

## Program Summary
The system uses a local **MQTT broker** (e.g., Mosquitto) for communication between the Raspberry Pi and ESP32 (via a middleware program).

### Simplified Algorithms
#### Raspberry Pi
![Simplified Algorithm of Raspberry Pi](https://github.com/Bhumipat001/FIBO-Academy-2025/blob/main/img/Algorithm%20inside%20Raspberry%20Pi.png)

#### ESP32
![Simplified Algorithm of ESP32](https://github.com/Bhumipat001/FIBO-Academy-2025/blob/main/img/Algorithm%20inside%20ESP32.png)

---

### Tracking Program
The repository includes an object detection model optimized from YOLOv8n. The program's goal is to move the focus object to the center of the screen.

![Algorithm of the Tracking Program](https://github.com/Bhumipat001/FIBO-Academy-2025/blob/main/img/Following%20Test.png)

---

### Radar Program
This implementation tests the radar's ability to sense a hand in front of the robot's face without physical contact. The radar uses the Doppler effect to detect motion.

![Algorithm of the Radar Program](https://github.com/Bhumipat001/FIBO-Academy-2025/blob/main/img/Radar%20Test.png)

**Note**: 
- The algorithm can be improved in many ways.
- The radar is more effective at detecting moving objects but may produce noise if the sensor itself moves.

For more details, refer to the [presentation slides](https://github.com/Bhumipat001/FIBO-Academy-2025/blob/main/Present%20Slide.pdf).

---
## Setup
Follow these steps to set up the system. Note that this is a basic setup and may require adjustments.

### Raspberry Pi Setup
**Distro**: Raspberry Pi OS (default username: `pi`)

1. **Update and Install Dependencies**  
   - Update the system and install required libraries.  
   - Enable SPI and UART pins via `raspi-config`.

2. **Create a Python Virtual Environment**  
   ```bash
   cd ~
   python3 -m venv RobotEnv
   ```

3. **Install Python Libraries**  
   Activate the virtual environment and install the required libraries.

4. **Clone the Raspberry Pi Code**  
   ```bash
   cd ~
   git clone https://github.com/Bhumipat001/FIBO-Academy-2025.git
   mv FIBO-Academy-2025/Desktop\ Friend\ Robot/Raspberry\ Pi\ 4/ ~/RobotFriend
   rm -rf ~/FIBO-Academy-2025
   ```

5. **Create and Enable a Systemd Service Unit File**  
   Set up a service to run the program automatically on boot.

6. **Test and Run the Program**  
   Start the program and ensure everything is working as expected.

---

### ESP32 Setup
1. **Install Required Libraries**  
   Install the necessary libraries in your Arduino IDE or other development environment.

2. **Upload the Code**  
   Flash the ESP32 with the provided code.

3. **Test the Setup**  
   Verify the ESP32 is communicating correctly with the Raspberry Pi.

---

**Note**: For both setups, patience and testing are key. Good luck! Gooses and Cats bless you🙏
