# Volume 1 — Chapter 3: MAVLink

> **Resources for the chapter "MAVLink: Drone Communication Protocol"**
> **Level:** Intermediate

---

## Overview

MAVLink (Micro Air Vehicle Link) is the standard communication protocol for drones. This directory contains scripts for:
- Reading telemetry in real time
- Analysing flight data
- Basic communication examples

All scripts work with Ardupilot, PX4 and other MAVLink-compatible firmware.

---

## Available Scripts

### 1. **telemetry_reader.py** — Real-Time Telemetry Reader ⭐
Script that continuously reads flight data and displays it.

```bash
python telemetry_reader.py
```

**Data displayed:**
- **GPS Position:** Latitude, Longitude, Altitude
- **Attitude:** Pitch, Roll, Yaw (angles)
- **Speed:** XYZ velocity
- **Battery:** Voltage, Current, % remaining
- **Status:** Armed/Disarmed, Flight mode, GPS satellites

---

### 2. **read_advanced_telemetry.py** — In-Depth Telemetry Analysis
More complete script that logs data and provides analysis.

```bash
python read_advanced_telemetry.py
```

**Features:**
- Records data to CSV for later analysis
- Calculates speed and acceleration
- Detects anomalies (low voltage, GPS loss, etc.)
- Flight statistics

---

### 3. **examples/connect_to_fc.py** — Basic Example
Minimal script to connect and read data.

```bash
python examples/connect_to_fc.py
```

---

## Installation

```bash
pip install -r requirements.txt
python telemetry_reader.py
```

---

## Testing in SITL

```bash
cd ~/ardupilot
./Tools/autotest/sim_vehicle.py -v ArduCopter -L default
# In another terminal:
python telemetry_reader.py
```

---

## Connecting to Hardware

```bash
python telemetry_reader.py --port /dev/ttyACM0 --baudrate 115200
```

---

## Resources

- **Book:** *Autonomous Drones I*, Volume 1, Chapter 3 — available on Amazon KDP
- **MAVLink specification:** https://mavlink.io/
- **pymavlink:** https://github.com/ArduPilot/pymavlink

---

**Last updated:** 16 April 2026
