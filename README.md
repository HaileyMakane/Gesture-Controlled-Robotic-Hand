# 🤖 GestureHand — Real-Time Robotic Hand Control via Hand Tracking

Control a servo-driven robotic hand in real time by mirroring your own hand's finger movements, powered by MediaPipe hand tracking and streamed over serial to an Arduino/ESP32.

---

## ✨ Key Features

- **Real-time hand tracking** using a single webcam feed (no special hardware needed on the vision side).
- **Per-finger bend estimation** computed from joint angles (MCP–PIP–DIP for four fingers, and the thumb's own joint chain).
- **Angle-to-servo mapping** that converts finger bend (0.0–1.0) into calibrated microsecond pulse widths for hobby servos.
- **Configurable calibration**: adjustable `MIN_US`/`MAX_US` pulse range and per-finger `INVERT` flags to correct for mechanical linkage direction.
- **Lightweight serial protocol**: a single comma-separated line (`thumb,index,middle,ring,pinky`) sent at a controlled rate (default ~30 FPS).
- **Live debug overlay** showing the exact values being transmitted, rendered directly on the camera feed.
- **Simple, dependency-light Python core** — easy to read, modify, and extend.

---

## 🛠️ Tech Stack

| Component | Library / Tool |
|---|---|
| Hand tracking & landmark detection | [MediaPipe](https://github.com/google-ai-edge/mediapipe) |
| Video capture & display | [OpenCV](https://opencv.org/) |
| Serial communication | [PySerial](https://pyserial.readthedocs.io/) |
| Angle/geometry math | Python's built-in `math` module |
| Microcontroller firmware target | Arduino / ESP32 (servo driver, not included in this repo) |

---

## 📦 Installation Guide

### 1. Clone the repository
```bash
git clone https://github.com/<your-username>/gesture-hand.git
cd gesture-hand
```

### 2. Create a virtual environment (recommended)
```bash
python -m venv venv

# Activate it:
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Connect your hardware
Plug in your Arduino/ESP32 controlling the servos via USB, and note the serial port it's assigned (see [Hardware Setup](#-hardware-setup) below).

---

## ▶️ Usage

1. Open `main.py` (or your script's filename) and set the correct serial port:
   ```python
   PORT = "COM3"  # Windows example
   # PORT = "/dev/ttyUSB0"  # Linux example
   # PORT = "/dev/ttyACM0"  # Linux/Mac example (ESP32/Arduino Uno)
   ```
2. Run the script:
   ```bash
   python main.py
   ```
3. A webcam window titled **"Hand -> ESP32 MG995"** will open.
4. Hold one hand in front of the camera:
   - **Open your fingers fully (straight)** → corresponding robotic finger extends.
   - **Curl a finger into a fist** → corresponding robotic finger closes.
   - Each finger (thumb, index, middle, ring, pinky) is tracked and mapped **independently**, so you can make custom poses (peace sign, pointing, etc.) and the hand will mirror them.
5. The current microsecond values being sent are overlaid on the video feed for live debugging.
6. Press **`ESC`** to quit the program safely.

### Calibration tips
- If a finger on the robotic hand moves in the *opposite* direction from your real finger, flip its value in the `INVERT` list.
- If bends feel too sensitive or not sensitive enough, tweak the `straight` and `closed` angle parameters passed to `bend_from_angle()` for that finger.
- Adjust `MIN_US`/`MAX_US` to match your specific servos' safe range.

---

## 🔧 Hardware Setup

> This section is a starting-point placeholder — update it with your exact wiring and BOM.

**Suggested components:**
- 1x Arduino Uno / ESP32 DevKit
- 5x hobby servos (e.g., MG995/MG996R — one per finger)
- External 5–6V power supply for servos (do **not** power all 5 servos from the microcontroller's 5V pin)
- Jumper wires, breadboard or custom PCB

**Suggested pin mapping** (adjust to match your firmware):

| Finger | Servo Signal Pin (example) |
|---|---|
| Thumb  | GPIO 13 |
| Index  | GPIO 12 |
| Middle | GPIO 14 |
| Ring   | GPIO 27 |
| Pinky  | GPIO 26 |

**Serial protocol expected by the firmware:**
```
<thumb_us>,<index_us>,<middle_us>,<ring_us>,<pinky_us>\n
```
Each value is a servo pulse width in microseconds (default range: `700`–`2000`). Your Arduino/ESP32 sketch should parse this comma-separated line and call `servo.writeMicroseconds(value)` for each finger accordingly.

**Power notes:**
- Share a common ground between the microcontroller and the servo power supply.
- Add flyback/decoupling capacitors near the servo power rail if you notice erratic behavior.

---

## 🗺️ Future Roadmap

- [ ] **Two-hand support** — extend `max_num_hands` and add multiplexed serial channels for dual robotic hands.
- [ ] **Gesture presets & recording** — save/replay specific hand poses as named macros (e.g., "thumbs up", "OK sign").
- [ ] **Wireless control** — replace wired serial with Bluetooth (BLE) or WiFi (ESP-NOW/MQTT) for an untethered robotic hand.
- [ ] **Auto-calibration routine** — an interactive script that guides the user through open/closed poses per finger to auto-derive `straight`/`closed` angle thresholds instead of manual tuning.

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
