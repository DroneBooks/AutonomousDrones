# Appendix Python — Educational Scripts

> **Educational Python scripts focused on drones**
> **Level:** Beginner → Intermediate

---

## Contents

```
Appendices/A2-Python/
├── README.md
├── requirements.txt
├── telemetry_basic.py              # ✅ Basic telemetry reading
├── color_detection_simple.py       # ✅ Simple HSV colour detection
└── advanced_example.py             # ✅ Telemetry + Vision in parallel
```

---

## Available Scripts

### 1. **telemetry_basic.py** — Basic Telemetry Reading ⭐
Simple script (30 lines) to read GPS, Battery and Attitude data.

```bash
python telemetry_basic.py
```

**Purpose:** Learn how to connect to a Flight Controller and read data.

**Data captured (30 seconds):**
- GPS: Latitude, Longitude, Altitude
- Battery: Voltage, Current, % remaining
- Attitude: Roll, Pitch, Yaw

**Ideal for:** First steps in drone-to-PC communication

---

### 2. **color_detection_simple.py** — HSV Colour Detection
Educational script that detects red colour in real time from a webcam.

```bash
python color_detection_simple.py
```

**Features:**
- Automatic red colour detection
- Noise filtering
- Displays contours and detected centroids
- Real-time FPS

**Controls:**
- `q` — Quit
- `c` — Calibrate colour (click on image)

**Ideal for:** Learning OpenCV and image processing

---

### 3. **advanced_example.py** — Telemetry + Vision in Parallel ⭐⭐
Advanced example combining pymavlink and OpenCV using threads,
with automatic CSV data logging.

```bash
python advanced_example.py
```

**Features:**
- MAVLink telemetry and OpenCV vision running simultaneously
- Independent threads for each module
- Red object detection annotated with altitude and battery data
- CSV log: `telemetry_vision_log.csv`
- Configurable duration (60 seconds by default)

**Controls:**
- `q` — Quit before time limit

**Ideal for:** Preparing for the Python Appendix Integrator Project

---

## Installation

```bash
# Step 1: Install dependencies
pip install -r requirements.txt

# Step 2: Run a script
python telemetry_basic.py
```

**Dependencies:**
- `pymavlink` — MAVLink communication
- `opencv-python` — Computer vision
- `numpy` — Numerical computations

---

## Quick Test

### Option 1: Without hardware (Simulator)
```bash
# Terminal 1: Start SITL
cd ~/ardupilot
./Tools/autotest/sim_vehicle.py -v ArduCopter

# Terminal 2: Run telemetry
python telemetry_basic.py
```

### Option 2: OpenCV only
```bash
python color_detection_simple.py
# Uses built-in webcam
```

---

## Appendix Python Content

| Lesson | Topic | Duration |
|--------|-------|----------|
| P.1 | Introduction to Python | 10 min |
| P.2 | Installation and Setup | 15 min |
| P.3 | Variables and Types | 15 min |
| P.4 | Functions and Modules | 20 min |
| P.5 | Drone Libraries | 20 min |
| P.6 | Project: Telemetry | 25 min |

**Total:** ~90 minutes of video

---

## Connecting to a Flight Controller

Scripts support:
- **SITL (simulation):** `127.0.0.1:14550`
- **USB:** `/dev/ttyUSB0` (Linux) or `COM3` (Windows)
- **Baud rate:** 57600 or 115200

---

## Requirements

- Python 3.10+
- Connection to SITL or Flight Controller (telemetry_basic.py)
- Camera connected (color_detection_simple.py)

---

## Troubleshooting

**"ModuleNotFoundError: No module named 'pymavlink'"**
```bash
pip install -r requirements.txt --upgrade
```

**"Cannot connect to 127.0.0.1:14550"**
- Verify SITL is running
- Try port 14551 if there are multiple instances

**"Camera not found"**
- Verify you have a webcam connected
- On Linux: `ls /dev/video*`

---

## Resources

- **Book:** *Autonomous Drones I*, Volume 1, Appendix A2 — available on Amazon KDP
- **PyMavLink Docs:** https://mavlink.io/
- **OpenCV Tutorials:** https://docs.opencv.org/

---

**Last updated:** 16 April 2026
**Author:** DroneAcademy Team
