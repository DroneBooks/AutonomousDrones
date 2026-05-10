# Chapter 4: ROS2 — Python Scripts

Scripts from **Chapter 4** of *Autonomous Drones II*.

## Prerequisites

- Ubuntu 22.04 LTS
- ROS2 Humble (install with `../install_ros2.sh`)
- MAVROS: `sudo apt install ros-humble-mavros ros-humble-mavros-msgs`
- Nav2: `sudo apt install ros-humble-nav2-bringup ros-humble-navigation2`

## Available Scripts

| Script | Description |
|--------|-------------|
| `publisher_simple.py` | Basic publisher node — publishes a string every second |
| `subscriber_simple.py` | Basic subscriber node — receives and logs messages |
| `drone_controller.py` | Drone control via MAVROS: GUIDED mode + arm |
| `flight_status_node.py` | Telemetry monitor: subscribes to 4 MAVROS topics, publishes JSON |
| `poi_navigator.py` | POI navigator with Nav2: flies to a list of (x, y, z) coordinates |

## Usage

```bash
# Source ROS2 before running any script
source /opt/ros/humble/setup.bash

# Terminal 1 — publisher
python3 publisher_simple.py

# Terminal 2 — subscriber (run simultaneously)
python3 subscriber_simple.py

# Drone controller (requires MAVROS + SITL running)
python3 drone_controller.py

# Flight status monitor (requires MAVROS)
python3 flight_status_node.py

# POI navigator (requires MAVROS + Nav2)
python3 poi_navigator.py
```

## SITL Quick Start

```bash
# Terminal 1: Ardupilot SITL
sim_vehicle.py -v ArduCopter -l 37.416,-122.144,14,0 -w --console

# Terminal 2: MAVROS bridge
ros2 launch mavros apm.launch fcu_url:=udp://@127.0.0.1:14550@

# Terminal 3: your script
source /opt/ros/humble/setup.bash
python3 drone_controller.py
```
