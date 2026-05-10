# Volume 1 — Chapter 2: Ardupilot

> **Resources for the chapter "Ardupilot: Autonomous Drone Firmware"**
> **Level:** Beginner to Intermediate

---

## Overview

This directory contains Python scripts for working with Ardupilot. They cover:
- Interactive sensor calibration
- Flight controller (FC) parameter configuration
- Basic connection and control examples

All scripts are designed to work with **SITL** (simulator) or real hardware.

---

## Available Scripts

### 1. **calibrate_sensors.py** — Sensor Calibration ⭐
Interactive assistant that guides you step by step through calibration:
- **Compass:** Magnetometer calibration
- **IMU:** Accelerometer/gyroscope calibration
- **Radio Control:** Channel mapping
- **ESC:** Motor speed calibration
- **Verification:** Sensor test

```bash
python calibrate_sensors.py
```

**Usage:** Follow the interactive prompts. Ideal for students who need to calibrate their drone.

---

### 2. **parameter_configurator.py** — Parameter Configurator
Interactive tool to read and write FC parameters.

```bash
python parameter_configurator.py
```

**Interactive menu:**
- List current parameters
- Change a parameter
- Search parameters by name
- Save configuration

**Example:** Adjust PID sensitivity, timeouts, etc.

---

### 3. **basic_connection.py** — Basic Connection
Minimal example to connect to a FC and read status.

```bash
python basic_connection.py
```

**Expected output:**
```
Connecting to 127.0.0.1:14550...
✓ Connected successfully!
Vehicle type: STANDBY
Current mode: STABILIZE
Armed: No
Armable: True
```

---

### 4. **change_mode.py** — Flight Mode Control
Switch between flight modes (Stabilize, Alt Hold, Loiter, etc.).

```bash
python change_mode.py
```

**Available modes:**
- STABILIZE (manual with stabilisation)
- ALT_HOLD (maintains altitude)
- LOITER (holds position)
- GUIDED (autonomous flight)
- LAND (automatic landing)

---

### 5. **takeoff_land.py** — Automatic Takeoff/Landing
Script for automatic takeoff and landing.

```bash
python takeoff_land.py
```

**Flow:**
1. Arms the drone (ARM)
2. Takes off to specified altitude
3. Waits for user input
4. Lands automatically

⚠️ **Caution:** Use in simulator first.

---

### 6. **waypoint_simple.py** — Waypoint Mission
Creates and executes a waypoint mission.

```bash
python waypoint_simple.py
```

**Features:**
- Defines waypoints (lat, lon, altitude)
- Uploads mission to FC
- Monitors flight progress
- Logs current position

---

### 7. **geofence_define.py** — Flight Boundaries
Sets up a safety perimeter (geofence).

```bash
python geofence_define.py
```

**Options:**
- Cylindrical geofence (radius/height)
- Rectangular geofence
- Maximum altitude
- Breach action (RTH, Land, etc.)

---

## Installing Dependencies

**Step 1:** Clone or download this directory

**Step 2:** Install dependencies
```bash
pip install -r requirements.txt
```

**Step 3:** Verify installation
```bash
python -c "import pymavlink; print(pymavlink.__version__)"
```

**Main dependencies:**
- `pymavlink` — MAVLink communication
- `pexpect` — Process interaction (SITL)
- `pyserial` — Serial communication (hardware)

---

## Testing in SITL (Simulator)

To test without hardware, use SITL (Software-in-the-Loop):

**Step 1:** Download Ardupilot
```bash
git clone https://github.com/ArduPilot/ardupilot
cd ardupilot
./Tools/autotest/sim_vehicle.py -v ArduCopter -L default
```

**Step 2:** In another terminal, run a script
```bash
python calibrate_sensors.py  # Connects to 127.0.0.1:14550
```

---

## Connecting to Real Hardware

**Option 1: Direct USB**
```bash
python calibrate_sensors.py
# Connects to /dev/ttyACM0 (Linux) or COM3 (Windows)
```

**Option 2: Serial Telemetry (FC → RPi/Laptop)**
```bash
python calibrate_sensors.py --port /dev/ttyUSB0 --baudrate 57600
```

**Option 3: Ethernet/WiFi (Advanced)**
Requires special FC configuration.

---

## System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| Python | 3.8 | 3.10+ |
| OS | Linux/Mac/Windows | Ubuntu 20.04 LTS |
| RAM | 1 GB | 4 GB |
| Storage | 500 MB | 2 GB |

---

## Safety Notes

1. **Simulator first:** Test all scripts in SITL before using with hardware
2. **Input validation:** Scripts validate ports and baud rates
3. **Port permissions:** On Linux, add your user to the `dialout` group:
   ```bash
   sudo usermod -a -G dialout $USER
   ```

---

## Troubleshooting

**"Connection refused"**
- Verify SITL is running (`sim_vehicle.py`)
- Check ports: `netstat -an | grep 14550`

**"Permission denied: /dev/ttyACM0"**
- On Linux: `sudo usermod -a -G dialout $USER` (requires logout/login)
- On Windows: Run terminal as administrator

**"pymavlink import error"**
- Reinstall: `pip install pymavlink --upgrade --force`

---

## Suggested Exercises

1. **Exercise 1:** Calibrate sensors in SITL and verify output
2. **Exercise 2:** Change the `ANGLE_MAX` parameter using parameter_configurator.py
3. **Exercise 3:** Run takeoff_land.py in the simulator
4. **Exercise 4:** Define a geofence and test a breach

---

## Related Resources

- **Book:** *Autonomous Drones I*, Volume 1, Chapter 2 — available on Amazon KDP
- **Ardupilot Documentation:** https://ardupilot.org/copter/docs/
- **Forum:** https://discuss.ardupilot.org/

---

**Last updated:** 16 April 2026
**Author:** DroneAcademy Team
