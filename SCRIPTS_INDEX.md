# Scripts Index — DroneBooks

> **Repository:** `AutonomousDrones`
> **Last updated:** May 2026
> **License:** All rights reserved — DroneBooks

All scripts are organised by **Volume** and **Chapter**, following the exact
numbering used in the books.

---

## Quick Navigation

### Volume 1 — *Autonomous Drones I: Hardware, Ardupilot and MAVLink*
- [Contents index (PDF)](VOLUME-1/volume1_index.pdf) — Preview before buying
- [Chapter 1: Hardware](#volume-1--chapter-1-hardware) — Specification calculators
- [Chapter 2: Ardupilot](#volume-1--chapter-2-ardupilot) — Calibration and configuration
- [Chapter 3: MAVLink](#volume-1--chapter-3-mavlink) — Telemetry and communication
- [Appendix A1: Git](#volume-1--appendix-a1-git) — Command quick reference
- [Appendix A2: Python](#volume-1--appendix-a2-python) — Educational Python scripts

### Volume 2 — *Autonomous Drones II: Robotics, Computer Vision and Embedded AI*
- [Contents index (PDF)](VOLUME-2/volume2_index.pdf) — Preview before buying
- [Chapter 1: ROS2](#volume-2--chapter-1-ros2) — Installer and robotics framework
- [Chapter 2: OpenCV + YOLO](#volume-2--chapter-2-opencv--yolo) — Computer vision
- [Chapter 3: AI in Drones](#volume-2--chapter-3-ai-in-drones) — Embedded AI on Jetson
- [Appendix A1: Git](#volume-2--appendix-a1-git) — Git for ROS2 projects
- [Appendix A2: C++](#volume-2--appendix-a2-c) — ROS2 nodes in C++

---

## Getting Started

```bash
# 1. Clone the complete repository
git clone https://github.com/DroneBooks/AutonomousDrones.git
cd AutonomousDrones

# 2. Install global dependencies
pip install -r requirements.txt

# 3. Navigate to the chapter you are reading, for example:
cd VOLUME-1/02-Ardupilot/Python/
python calibrate_sensors.py
```

---

## VOLUME 1 — Chapter 1: Hardware

📁 **Path:** `VOLUME-1/01-Hardware/`

### Available Files

| File | Description | Status |
|------|-------------|--------|
| `thrust_calculator.py` | Interactive specifications calculator | ✅ Ready |

### Included Calculators

```bash
cd VOLUME-1/01-Hardware/
python thrust_calculator.py
```

**Calculator menu:**
1. **Thrust-to-weight ratio (T:W)** — Does the drone have enough power?
2. **Flight time** — Endurance based on battery and power draw
3. **Motor selection (KV)** — Recommended KV range by drone category
4. **Blade tip speed** — Propeller safety check

**No external dependencies** — standard Python 3.10+ only.

---

## VOLUME 1 — Chapter 2: Ardupilot

📁 **Path:** `VOLUME-1/02-Ardupilot/Python/`

### Available Files

| File | Description | Status |
|------|-------------|--------|
| `calibrate_sensors.py` | Interactive calibration assistant | ✅ Ready |
| `parameter_configurator.py` | Read/write FC parameters | ✅ Ready |
| `basic_connection.py` | Connect and read telemetry | ✅ Ready |
| `takeoff_land.py` | Autonomous flight in GUIDED mode | ✅ Ready |
| `waypoint_simple.py` | Mission with 4 waypoints in a square | ✅ Ready |
| `change_mode.py` | Switch flight modes remotely | ✅ Ready |
| `geofence_define.py` | Create virtual flight boundaries | ✅ Ready |

### Typical Usage

```bash
cd VOLUME-1/02-Ardupilot/Python/
pip install -r requirements.txt

# Calibrate sensors (with FC connected)
python calibrate_sensors.py

# Flight in SITL (simulation)
python basic_connection.py --connect 127.0.0.1:14550
python takeoff_land.py --connect 127.0.0.1:14550 --alt 10 --time 5
python waypoint_simple.py --connect 127.0.0.1:14550 --alt 25
```

### Supported Connections

| Type | Connection string |
|------|------------------|
| SITL (simulation) | `127.0.0.1:14550` |
| USB Linux | `/dev/ttyUSB0` |
| USB Windows | `COM3` |
| Radio telemetry | `127.0.0.1:14551` |

---

## VOLUME 1 — Chapter 3: MAVLink

📁 **Path:** `VOLUME-1/03-MAVLink/Python/`

### Available Files

| File | Description | Status |
|------|-------------|--------|
| `telemetry_reader.py` | Continuous MAVLink telemetry reader | ✅ Ready |
| `read_advanced_telemetry.py` | Full telemetry with CSV export | ✅ Ready |
| `examples/connect_to_fc.py` | Minimal MAVLink connection example | ✅ Ready |

### Typical Usage

```bash
cd VOLUME-1/03-MAVLink/Python/
pip install -r requirements.txt

# Read real-time telemetry (SITL)
python telemetry_reader.py 127.0.0.1:14550 60

# Advanced telemetry with CSV export
python read_advanced_telemetry.py --connect 127.0.0.1:14550

# Basic connection example
python examples/connect_to_fc.py 127.0.0.1:14550
```

---

## VOLUME 1 — Appendix A1: Git

📁 **Path:** `VOLUME-1/Appendices/A1-Git/`

### Contents

Appendix A1 does not include Python scripts — Git is the tool itself.
The `README.md` contains a **quick reference of all commands** from the chapter:
- Initial setup, basic workflow, branches, remote repositories
- Recommended project structure for drones
- `.gitignore` for Python projects

```bash
cat VOLUME-1/Appendices/A1-Git/README.md
```

---

## VOLUME 1 — Appendix A2: Python

📁 **Path:** `VOLUME-1/Appendices/A2-Python/`

### Available Files

| File | Description | Level | Status |
|------|-------------|-------|--------|
| `telemetry_basic.py` | Basic GPS, battery and attitude reading | Beginner | ✅ Ready |
| `color_detection_simple.py` | Red colour detection with OpenCV | Beginner | ✅ Ready |
| `advanced_example.py` | Telemetry + vision in parallel (threads) | Intermediate | ✅ Ready |

### Typical Usage

```bash
cd VOLUME-1/Appendices/A2-Python/
pip install -r requirements.txt

# Script 1 — Basic telemetry (requires SITL or real FC)
python telemetry_basic.py

# Script 2 — Colour detection (requires camera)
python color_detection_simple.py

# Script 3 — Advanced example (both in parallel)
python advanced_example.py
```

---

## VOLUME 2 — Chapter 1: ROS2

📁 **Path:** `VOLUME-2/01-ROS2/`

### Available Files

| File | Description | Status |
|------|-------------|--------|
| `install_ros2.sh` | Automatic ROS2 Humble installer for Ubuntu 22.04 | ✅ Ready |

### Python Scripts

📁 **Path:** `VOLUME-2/01-ROS2/Python/`

| File | Description | Status |
|------|-------------|--------|
| `publisher_simple.py` | Basic publisher node — publishes a string every second | ✅ Ready |
| `subscriber_simple.py` | Basic subscriber node — receives and logs messages | ✅ Ready |
| `drone_controller.py` | Drone control via MAVROS: GUIDED mode + arm | ✅ Ready |
| `flight_status_node.py` | Telemetry monitor: subscribes to 4 MAVROS topics, publishes JSON | ✅ Ready |
| `poi_navigator.py` | POI navigator with Nav2: flies to a list of (x, y, z) coordinates | ✅ Ready |

### Usage

```bash
# Install ROS2 Humble on Ubuntu 22.04
bash VOLUME-2/01-ROS2/install_ros2.sh

# Verify installation
source /opt/ros/humble/setup.bash
ros2 --version

# Run example nodes (source ROS2 first)
cd VOLUME-2/01-ROS2/Python/
python3 publisher_simple.py    # Terminal 1
python3 subscriber_simple.py   # Terminal 2
```

The installer configures: ROS2 Humble Desktop, colcon, Python dependencies and `.bashrc`.

---

## VOLUME 2 — Chapter 2: OpenCV + YOLO

📁 **Path:** `VOLUME-2/02-OpenCV-YOLO/Python/`

### Available Files

| File | Description | Status |
|------|-------------|--------|
| `color_detection.py` | Configurable multi-colour HSV detection | ✅ Ready |
| `yolo_detection.py` | Object detection with YOLO v8 | ✅ Ready |

### Typical Usage

```bash
cd VOLUME-2/02-OpenCV-YOLO/Python/
pip install -r requirements.txt

# Colour detection (choose: red, green, blue, yellow)
python color_detection.py red

# YOLO on webcam (models: n, s, m, l, x)
python yolo_detection.py n          # Nano — fast, low resources
python yolo_detection.py m          # Medium — balanced

# YOLO on video file
python yolo_detection.py n video.mp4
```

### YOLO Model Performance

| Model | GPU (RTX) | CPU (i7) | Jetson Nano |
|-------|-----------|----------|-------------|
| Nano (n) | ~60 FPS | ~8 FPS | ~12 FPS |
| Small (s) | ~45 FPS | ~4 FPS | ~7 FPS |
| Medium (m) | ~30 FPS | ~2 FPS | ~3 FPS |

> **Note:** First run downloads the model (~6-50 MB depending on size).

---

## VOLUME 2 — Chapter 3: AI in Drones

📁 **Path:** `VOLUME-2/03-AI-Drones/`

### Available Files

| File | Description | Status |
|------|-------------|--------|
| `jetson_yolo_optimization.py` | Convert YOLO to TensorRT and compare latency | ✅ Ready |
| `latency_benchmark.py` | Detailed latency analysis (capture, preprocess, inference, postprocess) | ✅ Ready |
| `power_monitoring.py` | Real-time power consumption monitoring on Jetson | ✅ Ready |
| `drone_person_follower.py` | Drone that follows people with YOLO + distance estimation + PID control | ✅ Ready |
| `mission_analyzer.py` | Post-mission analysis: reports, timeline and GPS export of detections | ✅ Ready |

### Typical Usage

```bash
cd VOLUME-2/03-AI-Drones/
pip install -r requirements.txt

# Optimise model to TensorRT and measure improvement
python jetson_yolo_optimization.py --model yolov8n.pt

# Analyse full latency breakdown
python latency_benchmark.py --model yolov8n.pt --source dummy --frames 100

# Monitor power consumption
python power_monitoring.py --model yolov8n.pt --frames 100 --export-csv power.csv
```

### Key Concepts (from the Chapter)

- **TensorRT:** NVIDIA inference engine that accelerates YOLO models 2-10x
- **Latency:** Total pipeline time (< 100ms recommended for drones)
- **Power:** Energy consumption on embedded platforms (critical for endurance)

---

## VOLUME 2 — Appendix A1: Git

📁 **Path:** `VOLUME-2/Appendices/A1-Git/`

Git quick reference applied to **ROS2 and C++** projects.
Includes a ROS2-specific `.gitignore` and recommended package structure.

```bash
cat VOLUME-2/Appendices/A1-Git/README.md
```

---

## VOLUME 2 — Appendix A2: C++

📁 **Path:** `VOLUME-2/Appendices/A2-Cpp/`

### Available Files

| File | Description | Status |
|------|-------------|--------|
| `publisher_node.cpp` | ROS2 publisher node for telemetry (altitude, battery, speed) | ✅ Ready |
| `subscriber_node.cpp` | ROS2 subscriber node with control logic and alerts | ✅ Ready |
| `bridge_mavlink.cpp` | MAVLink ↔ ROS2 bridge for Pixhawk integration | ✅ Ready |
| `CMakeLists.txt` | Build template for C++ nodes in ROS2 | ✅ Ready |

### Typical Usage

```bash
cd VOLUME-2/Appendices/A2-Cpp/

# Prepare ROS2 workspace
mkdir -p ~/ros2_ws/src
cp -r . ~/ros2_ws/src/drone_telemetry

# Build
cd ~/ros2_ws
colcon build --packages-select drone_telemetry

# Run nodes
source install/setup.bash
ros2 run drone_telemetry publisher_node    # Terminal 1
ros2 run drone_telemetry subscriber_node   # Terminal 2
ros2 run drone_telemetry bridge_mavlink    # Terminal 3 (optional)
```

### Key Concepts (from the Appendix)

- **ROS2 Nodes:** Independent processes communicating via topics
- **Publishers/Subscribers:** Pub-sub patterns for telemetry and commands
- **MAVLink Bridge:** Translation between binary protocol and ROS2 topics
- **CMake:** Build system for complex C++ projects

---

## Complete Repository Structure

```
AutonomousDrones/
│
├── README.md                              ← Entry point
├── SCRIPTS_INDEX.md                       ← This file
├── requirements.txt                       ← Global dependencies
│
├── VOLUME-1/                              # Autonomous Drones I
│   ├── volume1_index.pdf                  📄 Full index (preview)
│   ├── 01-Hardware/
│   │   ├── README.md
│   │   └── thrust_calculator.py           ✅
│   ├── 02-Ardupilot/Python/
│   │   ├── README.md
│   │   ├── requirements.txt
│   │   ├── calibrate_sensors.py           ✅
│   │   ├── parameter_configurator.py      ✅
│   │   ├── basic_connection.py            ✅
│   │   ├── takeoff_land.py                ✅
│   │   ├── waypoint_simple.py             ✅
│   │   ├── change_mode.py                 ✅
│   │   └── geofence_define.py             ✅
│   ├── 03-MAVLink/Python/
│   │   ├── README.md
│   │   ├── requirements.txt
│   │   ├── telemetry_reader.py            ✅
│   │   ├── read_advanced_telemetry.py     ✅
│   │   └── examples/
│   │       └── connect_to_fc.py           ✅
│   └── Appendices/
│       ├── A1-Git/
│       │   └── README.md                  ✅ Quick reference
│       └── A2-Python/
│           ├── README.md
│           ├── requirements.txt
│           ├── telemetry_basic.py          ✅
│           ├── color_detection_simple.py   ✅
│           └── advanced_example.py         ✅
│
└── VOLUME-2/                              # Autonomous Drones II
    ├── volume2_index.pdf                  📄 Full index (preview)
    ├── 01-ROS2/
    │   ├── install_ros2.sh                ✅
    │   └── Python/
    │       ├── README.md
    │       ├── publisher_simple.py        ✅
    │       ├── subscriber_simple.py       ✅
    │       ├── drone_controller.py        ✅
    │       ├── flight_status_node.py      ✅
    │       └── poi_navigator.py           ✅
    ├── 02-OpenCV-YOLO/Python/
    │   ├── README.md
    │   ├── requirements.txt
    │   ├── color_detection.py             ✅
    │   └── yolo_detection.py              ✅
    ├── 03-AI-Drones/
    │   ├── README.md                      ✅
    │   ├── requirements.txt               ✅
    │   ├── jetson_yolo_optimization.py    ✅
    │   ├── latency_benchmark.py           ✅
    │   ├── power_monitoring.py            ✅
    │   ├── drone_person_follower.py       ✅
    │   └── mission_analyzer.py            ✅
    └── Appendices/
        ├── A1-Git/
        │   └── README.md                  ✅ ROS2 quick reference
        └── A2-Cpp/
            ├── README.md                  ✅
            ├── CMakeLists.txt             ✅
            ├── publisher_node.cpp         ✅
            ├── subscriber_node.cpp        ✅
            └── bridge_mavlink.cpp         ✅
```

---

## Global Requirements

| Component | Minimum version |
|-----------|----------------|
| Python | 3.10+ |
| Ubuntu (recommended) | 22.04 LTS |
| ROS2 (Vol.2 Ch.1+ only) | Humble |
| GPU (YOLO at speed only) | NVIDIA with CUDA |

---

## Common Issues

### "ModuleNotFoundError"
```bash
pip install -r requirements.txt
```

### "Cannot connect to 127.0.0.1:14550"
```bash
# Start SITL first
sim_vehicle.py -v ArduCopter --location=-35.362882,149.165230,584,0
```

### "Camera not found"
```bash
ls /dev/video*   # Linux — identify your camera
```

### "Port /dev/ttyUSB0 not found"
```bash
ls /dev/tty*     # Linux
```

---

## Support

- **Issues:** https://github.com/DroneBooks/AutonomousDrones/issues

---

**© 2026 DroneBooks — All rights reserved**
