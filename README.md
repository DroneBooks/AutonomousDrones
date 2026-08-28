> 🇪🇸 **Versión en español:** [DronesAutonomos](https://github.com/DroneBooks/DronesAutonomos) · 🌐 [dronebooks.eu](https://dronebooks.eu)

# Autonomous Drones — Code Repository

**Companion resources for the books Volume 1: 'Autonomous Drones I:
Hardware, Ardupilot, MAVLink' and Volume 2: 'Autonomous Drones II:
Robotics, Computer Vision, AI'**

[![GitHub](https://img.shields.io/badge/GitHub-DroneBooks-blue?logo=github)](https://github.com/DroneBooks)
![License](https://img.shields.io/badge/License-All%20rights%20reserved-red)

---

## About This Repository

This repository contains all **example scripts, reference code, training data and installers** that accompany the two main DroneBooks volumes.

### Target Audience
- Junior/mid-level engineers specialising in autonomous drones
- Advanced makers with electronics and programming experience
- Robotics and Computer Science engineering students

---

## Table of Contents (Preview)

Before buying, you can browse the full index of each volume:

| Volume | PDF | Pages |
|--------|-----|-------|
| Autonomous Drones I | [volume1_index.pdf](VOLUME-1/volume1_index.pdf) | 7 pp. |
| Autonomous Drones II | [volume2_index.pdf](VOLUME-2/volume2_index.pdf) | 7 pp. |

---

## Repository Structure

```
AutonomousDrones/
│
├── VOLUME-1/                           # Autonomous Drones I
│   ├── volume1_index.pdf               # Full contents index (preview)
│   ├── 01-Hardware/
│   │   └── thrust_calculator.py        # T:W, flight time, KV, propeller
│   ├── 02-Ardupilot/Python/            # 7 scripts: calibrate, waypoints, etc.
│   ├── 03-MAVLink/Python/              # telemetry, read_advanced_telemetry
│   └── Appendices/
│       ├── A1-Git/                     # Git quick reference
│       └── A2-Python/                  # 3 scripts: telemetry, color, advanced
│
├── VOLUME-2/                           # Autonomous Drones II
│   ├── volume2_index.pdf               # Full contents index (preview)
│   ├── 01-ROS2/
│   │   └── install_ros2.sh             # Automatic ROS2 Humble installer
│   ├── 02-OpenCV-YOLO/Python/          # color_detection.py, yolo_detection.py
│   ├── 03-AI-Drones/                   # 5 scripts: optimisation, latency, power, follower, analyser
│   └── Appendices/
│       ├── A1-Git/                     # Git for ROS2 projects
│       └── A2-Cpp/                     # 4 files: publisher, subscriber, bridge MAVLink, CMakeLists
│
├── README.md                           (This file)
├── SCRIPTS_INDEX.md                    (Full catalogue with paths and examples)
└── requirements.txt                    (Global Python dependencies)
```

---

## Quick Start

### Volume 1 (Fundamentals)
```bash
# 1. Clone the repo
git clone https://github.com/DroneBooks/AutonomousDrones.git
cd AutonomousDrones

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Go to Volume 1 scripts
cd VOLUME-1/02-Ardupilot/Python
python3 calibrate_sensors.py
```

### Volume 2 (Robotics & AI)
```bash
# 1. Clone the repo
git clone https://github.com/DroneBooks/AutonomousDrones.git
cd AutonomousDrones

# 2. Install ROS2 Humble
bash VOLUME-2/01-ROS2/install_ros2.sh

# 3. Try computer vision
cd VOLUME-2/02-OpenCV-YOLO/Python
python3 yolo_detection.py
```

---

## Learning Path

### Volume 1 — *Autonomous Drones I: Hardware, Ardupilot and MAVLink*
```
Read Chapter 1 (Hardware)
    ↓
Run: VOLUME-1/01-Hardware/thrust_calculator.py
    ↓
Read Chapter 2 (Ardupilot)
    ↓
Run: VOLUME-1/02-Ardupilot/Python/calibrate_sensors.py
     VOLUME-1/02-Ardupilot/Python/waypoint_simple.py
    ↓
Read Chapter 3 (MAVLink)
    ↓
Run: VOLUME-1/03-MAVLink/Python/telemetry_reader.py
     VOLUME-1/03-MAVLink/Python/read_advanced_telemetry.py
    ↓
Read Appendix A1 (Git) — reference: VOLUME-1/Appendices/A1-Git/README.md
    ↓
Read Appendix A2 (Python)
    ↓
Run: VOLUME-1/Appendices/A2-Python/telemetry_basic.py
     VOLUME-1/Appendices/A2-Python/advanced_example.py
```

### Volume 2 — *Autonomous Drones II: Robotics, Computer Vision and Embedded AI*
```
Read Chapter 1 (ROS2)
    ↓
Run: bash VOLUME-2/01-ROS2/install_ros2.sh
    ↓
Read Chapter 2 (OpenCV + YOLO)
    ↓
Run: VOLUME-2/02-OpenCV-YOLO/Python/color_detection.py red
     VOLUME-2/02-OpenCV-YOLO/Python/yolo_detection.py n
    ↓
Read Chapter 3 (AI in Drones)
    ↓
Run: VOLUME-2/03-AI-Drones/jetson_yolo_optimization.py
     VOLUME-2/03-AI-Drones/latency_benchmark.py
     VOLUME-2/03-AI-Drones/power_monitoring.py
     VOLUME-2/03-AI-Drones/drone_person_follower.py
     VOLUME-2/03-AI-Drones/mission_analyzer.py
    ↓
Read Appendix A1 (Git) — reference: VOLUME-2/Appendices/A1-Git/README.md
    ↓
Read Appendix A2 (C++)
    ↓
Build: VOLUME-2/Appendices/A2-Cpp/publisher_node.cpp  (compile + run)
       VOLUME-2/Appendices/A2-Cpp/subscriber_node.cpp
       VOLUME-2/Appendices/A2-Cpp/bridge_mavlink.cpp
```

---

## Available Scripts

### VOLUME-1 — *Autonomous Drones I*
| Resource | Chapter / Appendix | Path | Description |
|----------|--------------------|------|-------------|
| `thrust_calculator.py` | Ch. 1: Hardware | `VOLUME-1/01-Hardware/` | T:W, flight time, KV, propeller |
| `calibrate_sensors.py` | Ch. 2: Ardupilot | `VOLUME-1/02-Ardupilot/Python/` | Calibrates IMU, compass, ESC |
| `parameter_configurator.py` | Ch. 2: Ardupilot | `VOLUME-1/02-Ardupilot/Python/` | Read/write FC parameters |
| `basic_connection.py` | Ch. 2-3 | `VOLUME-1/02-Ardupilot/Python/` | Connection and basic telemetry |
| `takeoff_land.py` | Ch. 2-3 | `VOLUME-1/02-Ardupilot/Python/` | Autonomous flight in GUIDED |
| `waypoint_simple.py` | Ch. 2-3 | `VOLUME-1/02-Ardupilot/Python/` | Mission with 4 waypoints |
| `change_mode.py` | Ch. 2-3 | `VOLUME-1/02-Ardupilot/Python/` | Change flight modes |
| `geofence_define.py` | Ch. 2-3 | `VOLUME-1/02-Ardupilot/Python/` | Virtual flight boundary |
| `telemetry_reader.py` | Ch. 3: MAVLink | `VOLUME-1/03-MAVLink/Python/` | Real-time telemetry |
| `read_advanced_telemetry.py` | Ch. 3: MAVLink | `VOLUME-1/03-MAVLink/Python/` | Telemetry + CSV export |
| `README.md` | Appendix A1: Git | `VOLUME-1/Appendices/A1-Git/` | Git quick reference |
| `telemetry_basic.py` | Appendix A2: Python | `VOLUME-1/Appendices/A2-Python/` | Basic educational telemetry |
| `color_detection_simple.py` | Appendix A2: Python | `VOLUME-1/Appendices/A2-Python/` | HSV color detection |
| `advanced_example.py` | Appendix A2: Python | `VOLUME-1/Appendices/A2-Python/` | Telemetry + vision in parallel |

### VOLUME-2 — *Autonomous Drones II*
| Resource | Chapter / Appendix | Path | Description |
|----------|--------------------|------|-------------|
| `install_ros2.sh` | Ch. 1: ROS2 | `VOLUME-2/01-ROS2/` | ROS2 Humble installer |
| `color_detection.py` | Ch. 2: OpenCV+YOLO | `VOLUME-2/02-OpenCV-YOLO/Python/` | Multi-colour HSV detection |
| `yolo_detection.py` | Ch. 2: OpenCV+YOLO | `VOLUME-2/02-OpenCV-YOLO/Python/` | Object detection with YOLOv8 |
| `jetson_yolo_optimization.py` | Ch. 3: AI Drones | `VOLUME-2/03-AI-Drones/` | TensorRT optimisation |
| `latency_benchmark.py` | Ch. 3: AI Drones | `VOLUME-2/03-AI-Drones/` | Latency measurement |
| `power_monitoring.py` | Ch. 3: AI Drones | `VOLUME-2/03-AI-Drones/` | Power consumption monitoring |
| `drone_person_follower.py` | Ch. 3: AI Drones | `VOLUME-2/03-AI-Drones/` | Person follower drone |
| `mission_analyzer.py` | Ch. 3: AI Drones | `VOLUME-2/03-AI-Drones/` | Post-mission analysis |
| `README.md` | Appendix A1: Git | `VOLUME-2/Appendices/A1-Git/` | Git for ROS2 projects |
| `publisher_node.cpp` | Appendix A2: C++ | `VOLUME-2/Appendices/A2-Cpp/` | ROS2 publisher node |
| `subscriber_node.cpp` | Appendix A2: C++ | `VOLUME-2/Appendices/A2-Cpp/` | ROS2 subscriber node |
| `bridge_mavlink.cpp` | Appendix A2: C++ | `VOLUME-2/Appendices/A2-Cpp/` | MAVLink-ROS2 bridge |
| `CMakeLists.txt` | Appendix A2: C++ | `VOLUME-2/Appendices/A2-Cpp/` | C++ ROS2 build template |

See **SCRIPTS_INDEX.md** for the full catalogue with detailed descriptions.

---

## System Requirements

### Minimum Hardware
- **CPU:** Intel i5 / Ryzen 5 (for simulation)
- **RAM:** 8 GB
- **GPU:** RTX 3060+ (recommended for YOLO)
- **Drone:** Pixhawk 6C with Ardupilot 4.5+

### Software
- **OS:** Ubuntu 22.04 LTS (recommended)
- **Python:** 3.10+
- **Git:** to clone this repo
- **ROS2:** Humble (installer included in VOLUME-2/01-ROS2/)

---

## Contact & Support

- **GitHub:** [@DroneBooks](https://github.com/DroneBooks)
- **Issues/Questions:** https://github.com/DroneBooks/AutonomousDrones/issues

---

**Version:** 1.1 | **Last updated:** May 2026
