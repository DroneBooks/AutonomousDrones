# Volume 2 — Chapter 2: OpenCV + YOLO

> **Resources for the chapter "Computer Vision: OpenCV and YOLO on Drones"**
> **Level:** Intermediate to Advanced

---

## Overview

Computer vision is critical for autonomous drones. This directory contains scripts for:
- Colour detection (classical methods)
- Object detection with deep learning (YOLO v8)
- Real-time image processing

Includes both traditional methods and neural networks.

---

## Available Scripts

### 1. **color_detection.py** — HSV Colour Detection ⭐
Interactive script that detects specific colours using the HSV colour space.

```bash
python color_detection.py
```

**Supported colours:**
- Red, Green, Blue, Yellow
- Adjustable HSV range
- Real-time mask
- FPS display

**Usage:** Ideal for beginners learning image processing.

---

### 2. **yolo_detection.py** — Real-Time YOLO v8 Detection
Script running YOLOv8 to detect 80+ objects.

```bash
python yolo_detection.py
```

**Features:**
- Detection of people, vehicles, animals, etc.
- Bounding boxes around objects
- FPS and latency display
- Detection confidence score

**Available models:**
- `yolov8n.pt` (Nano — fast, less accurate)
- `yolov8s.pt` (Small — balanced)
- `yolov8m.pt` (Medium — accurate, slower)

---

### 3. **examples/basic_detection.py** — Educational Example
Minimal script showing the basic detection structure.

```bash
python examples/basic_detection.py
```

---

## Installing Dependencies

**Step 1:** Install dependencies
```bash
pip install -r requirements.txt
```

**Step 2:** Download YOLO model (automatic on first run)
```bash
python yolo_detection.py
# Downloads yolov8n.pt (~6 MB)
```

**Main dependencies:**
- `opencv-python` — Image processing
- `numpy` — Numerical computations
- `ultralytics` — YOLO framework
- `torch` — Deep Learning

---

## Basic Test

```bash
# Test with webcam
python color_detection.py     # Press 'q' to quit
python yolo_detection.py

# Test with image
python yolo_detection.py --image test.jpg

# Test with video
python yolo_detection.py --video test.mp4
```

---

## Comparison: Classical Methods vs YOLO

| Aspect | HSV (Classical) | YOLO v8 |
|--------|----------------|---------|
| **Speed** | 30-60 FPS | 10-60 FPS* |
| **Accuracy** | Light-sensitive | 80%+ mAP |
| **Flexibility** | 1 colour/script | 80+ objects |
| **Resources** | CPU | GPU recommended |
| **Complexity** | Low | Medium-High |

*Depends on hardware and model

---

## Optimisation for Drones

To run on constrained hardware (Jetson Nano):

```bash
# Use Nano model
python yolo_detection.py --model yolov8n.pt

# With FP16 (half precision = faster)
python yolo_detection.py --half

# Reduce resolution
python yolo_detection.py --imgsz 320
```

---

## Use Cases

1. **Person detection:** Security, rescue, agriculture
2. **Aerial mapping:** Building count, crop analysis
3. **Inspection:** Finding objects/anomalies
4. **Tracking:** Following moving targets

---

## Limitations

1. **Lighting:** HSV is very sensitive to light changes
2. **Latency:** YOLO adds 50-100ms (critical in close flight)
3. **Resources:** GPU recommended for real-time on drone
4. **Accuracy:** YOLO is not 100% (typically 80-90%)

---

## Troubleshooting

**"No camera found"**
```bash
ls /dev/video*  # Linux
# If nothing appears, install UVC:
sudo apt install libopencv-dev
```

**"YOLO model download failed"**
```bash
# Download manually
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt
```

**"Out of memory"**
- Use a smaller model (yolov8n)
- Reduce imgsz to 320
- Run on GPU if available

---

## Performance Metrics

Running `python yolo_detection.py` shows:
- **FPS:** Frames processed per second
- **Latency:** Detection time in ms
- **Confidence:** % certainty of detection

---

## Resources

- **Book:** *Autonomous Drones II*, Volume 2, Chapter 2 — available on Amazon KDP
- **Ultralytics YOLO:** https://github.com/ultralytics/ultralytics
- **OpenCV Docs:** https://docs.opencv.org/
- **NVIDIA Jetson:** https://docs.nvidia.com/jetson/

---

**Last updated:** 16 April 2026
**Author:** DroneAcademy Team
