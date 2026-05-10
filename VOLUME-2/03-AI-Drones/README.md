# Volume 2 — Chapter 3: AI in Drones

> **Resources for the chapter "Embedded Artificial Intelligence in Drones"**
> **Level:** Advanced
> **Last updated:** May 2026

---

## Contents

```
VOLUME-2/03-AI-Drones/
├── jetson_yolo_optimization.py    # ✅ Convert YOLO to TensorRT
├── latency_benchmark.py           # ✅ Measure inference latency
├── power_monitoring.py            # ✅ Monitor power consumption
├── drone_person_follower.py       # ✅ Person-following drone
├── mission_analyzer.py            # ✅ Post-mission analysis
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

---

## Available Scripts

| Script | Description | Status |
|--------|-------------|--------|
| `jetson_yolo_optimization.py` | TensorRT conversion on Jetson Nano/Orin | ✅ Ready |
| `latency_benchmark.py` | Measure inference latency by model | ✅ Ready |
| `power_monitoring.py` | Real-time power consumption monitoring | ✅ Ready |
| `drone_person_follower.py` | Person-following with YOLO + PID control | ✅ Ready |
| `mission_analyzer.py` | Post-mission reports and GPS detection export | ✅ Ready |

---

## Usage Guide

### Quick Installation

```bash
cd VOLUME-2/03-AI-Drones/
pip install -r requirements.txt
```

### 1️⃣ TensorRT Optimisation

Converts a YOLO model to optimised TensorRT format (2-10x faster):

```bash
# Convert and compare latency
python jetson_yolo_optimization.py --model yolov8n.pt

# With more workspace for additional speed
python jetson_yolo_optimization.py --model yolov8m.pt --workspace 4

# Benchmark only (without converting)
python jetson_yolo_optimization.py --model yolov8n.pt --benchmark-only
```

**Expected output:**
- Shows original vs TensorRT latency
- Calculates speedup factor
- Saves `.engine` model for future use

### 2️⃣ Latency Analysis

Measures full pipeline latency broken down by component:

```bash
# Use webcam (requires --source webcam)
python latency_benchmark.py --model yolov8n.pt --source webcam --frames 100

# Process video
python latency_benchmark.py --model yolov8n.pt --source video.mp4

# Use dummy images (no hardware required)
python latency_benchmark.py --model yolov8n.pt --source dummy --frames 200

# Export data and plots
python latency_benchmark.py --model yolov8n.pt --export-csv latencies.csv --plot latency.png
```

**Latency breakdown:**
- ⏱️ Capture: camera/file read time
- ⏱️ Preprocess: resize and normalisation
- ⏱️ Inference: model forward pass
- ⏱️ Postprocess: detection extraction

### 3️⃣ Power Monitoring

Measures actual power consumption during inference (Jetson with `jetson-stats` only):

```bash
# Basic monitoring
python power_monitoring.py --model yolov8n.pt --frames 100

# Extended monitoring (60 seconds)
python power_monitoring.py --model yolov8m.pt --duration 60

# Export data
python power_monitoring.py --model yolov8n.pt --export-csv power.csv --plot power.png
```

**Information included:**
- Average, minimum and maximum power
- Energy consumed (Joules, Wh)
- Estimated drone endurance with different battery sizes
- GPU temperature (if available)

---

## Chapter Requirements

### Recommended Hardware
- **NVIDIA Jetson Nano** (4 GB) or **Jetson Orin NX** (8 GB)
- CSI camera (Raspberry Pi Camera v2 or similar)
- Pixhawk 6C with Ardupilot 4.5+

### Software
```bash
# On Jetson: JetPack 5.1+ (includes CUDA, cuDNN, TensorRT)
# Python 3.10+
pip install ultralytics pymavlink opencv-python numpy
```

### Verify GPU availability
```python
import torch
print(torch.cuda.is_available())    # True if Jetson has CUDA
print(torch.cuda.get_device_name()) # GPU name
```

---

## Meanwhile: Use OpenCV+YOLO Scripts

The Chapter 2 scripts also serve as a base for this chapter:

```bash
# From the repository root
cd VOLUME-2/02-OpenCV-YOLO/Python/

# YOLO detection (works on CPU and GPU)
python yolo_detection.py n        # Nano — ideal for Jetson
python yolo_detection.py s        # Small
```

---

## Book Reference

This chapter accompanies **Volume 2, Chapter 3: AI in Drones** of the book
*Autonomous Drones II: Robotics, Computer Vision and Embedded AI*.

Topics covered in the chapter:
- Cloud AI vs embedded AI
- Model optimisation with TensorRT (Jetson)
- Integrating inference with flight control (MAVLink)
- Power consumption and latency on embedded platforms

---

**Last updated:** April 2026 | DroneBooks
