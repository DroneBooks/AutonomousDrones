# Volume 2 — Appendix A2: C++ for ROS2

> **Resources for the appendix "C++: High-Performance ROS2 Node Development"**
> **Level:** Intermediate to Advanced

---

## Contents

```
VOLUME-2/Appendices/A2-Cpp/
├── README.md                 # This guide
├── CMakeLists.txt            # Build template
├── publisher_node.cpp        # Telemetry publisher
├── subscriber_node.cpp       # Subscriber with control logic
├── bridge_mavlink.cpp        # MAVLink ↔ ROS2 bridge
└── src/                      # (create when cloning the repo)
    ├── publisher_node.cpp
    ├── subscriber_node.cpp
    └── bridge_mavlink.cpp
```

---

## Available Examples

| File | Description | Status |
|------|-------------|--------|
| `publisher_node.cpp` | Basic ROS2 publisher node in C++ | ✅ Ready |
| `subscriber_node.cpp` | Basic ROS2 subscriber node in C++ | ✅ Ready |
| `CMakeLists.txt` | Build template for C++ nodes | ✅ Ready |
| `bridge_mavlink.cpp` | MAVLink ↔ ROS2 topics bridge in C++ | ✅ Ready |

---

## Installing ROS2 (Prerequisite)

Before compiling any C++ node, install ROS2 Humble using the included script:

```bash
# From the repository root
bash VOLUME-2/01-ROS2/install_ros2.sh
```

The script automatically installs:
- ROS2 Humble Desktop
- Build tools (colcon, cmake)
- ROS2 Python dependencies

---

## C++ ROS2 Node Structure

```cpp
// Minimal example — telemetry publisher
#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/float64.hpp"

class TelemetryNode : public rclcpp::Node {
public:
    TelemetryNode() : Node("telemetry") {
        publisher_ = create_publisher<std_msgs::msg::Float64>(
            "altitude", 10);
        timer_ = create_wall_timer(
            std::chrono::milliseconds(500),
            std::bind(&TelemetryNode::publish, this));
    }

private:
    void publish() {
        auto msg = std_msgs::msg::Float64();
        msg.data = 25.3;  // In production: read from MAVLink
        publisher_->publish(msg);
        RCLCPP_INFO(get_logger(), "Altitude: %.1f m", msg.data);
    }
    rclcpp::Publisher<std_msgs::msg::Float64>::SharedPtr publisher_;
    rclcpp::TimerBase::SharedPtr timer_;
};

int main(int argc, char* argv[]) {
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<TelemetryNode>());
    rclcpp::shutdown();
    return 0;
}
```

### Minimal CMakeLists.txt
```cmake
cmake_minimum_required(VERSION 3.8)
project(telemetry_node)

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)

add_executable(telemetry_node src/telemetry_node.cpp)
ament_target_dependencies(telemetry_node rclcpp std_msgs)

install(TARGETS telemetry_node DESTINATION lib/${PROJECT_NAME})
ament_package()
```

### Build and run

**Step 1: Prepare workspace**
```bash
# Create ROS2 workspace if it does not exist
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src

# Clone or copy the drone_telemetry package
git clone https://github.com/DroneBooks/AutonomousDrones.git
cd ..
```

**Step 2: Copy files to the correct location**
```bash
# Expected structure:
# ~/ros2_ws/src/drone_telemetry/
# ├── CMakeLists.txt
# ├── package.xml
# ├── src/
# │   ├── publisher_node.cpp
# │   ├── subscriber_node.cpp
# │   └── bridge_mavlink.cpp
```

**Step 3: Create package.xml** (if it does not exist)
```bash
cd ~/ros2_ws/src/drone_telemetry
cat > package.xml << 'EOF'
<?xml version="1.0"?>
<package format="3">
  <name>drone_telemetry</name>
  <version>0.0.1</version>
  <description>ROS2 C++ nodes for drone telemetry</description>
  <maintainer email="student@droneacademy.local">Student</maintainer>
  <license>BSD-3-Clause</license>
  <buildtool_depend>ament_cmake</buildtool_depend>
  <depend>rclcpp</depend>
  <depend>std_msgs</depend>
  <depend>geometry_msgs</depend>
</package>
EOF
```

**Step 4: Build**
```bash
cd ~/ros2_ws
colcon build --packages-select drone_telemetry

# Build with verbose output if there are errors:
colcon build --packages-select drone_telemetry --cmake-args -DCMAKE_BUILD_TYPE=Debug
```

**Step 5: Run nodes**
```bash
# Terminal 1: Publisher
source ~/ros2_ws/install/setup.bash
ros2 run drone_telemetry publisher_node

# Terminal 2: Subscriber
source ~/ros2_ws/install/setup.bash
ros2 run drone_telemetry subscriber_node

# Terminal 3: MAVLink Bridge (optional, requires Pixhawk or SITL)
source ~/ros2_ws/install/setup.bash
ros2 run drone_telemetry bridge_mavlink --connect 127.0.0.1:14550
```

**Step 6: Monitor topics**
```bash
# Terminal 4: List published topics
source ~/ros2_ws/install/setup.bash
ros2 topic list

# View content in real time
ros2 topic echo /telemetry/altitude
ros2 topic echo /telemetry/battery
ros2 topic echo /telemetry/speed
```

---

## Python vs C++ in ROS2

| Feature | Python | C++ |
|---------|--------|-----|
| Development speed | ✅ Fast | Slow |
| Real-time performance | Limited | ✅ Optimal |
| Memory management | Automatic | Manual |
| Use in critical controllers | Not recommended | ✅ Ideal |
| Learning curve | Low | High |

> **Golden rule:** Python for prototyping, C++ for production.

---

## Book Reference

This appendix accompanies **Volume 2, Appendix A2: C++** of the book
*Autonomous Drones II: Robotics, Computer Vision and Embedded AI*.

Topics covered in the appendix:
- Essential C++ syntax for robotics (pointers, references, classes)
- Publisher/subscriber nodes in C++
- ROS2 services and actions in C++
- MAVLink integration with ROS2 in C++
- CMake and colcon for building

---

## Requirements

- **OS:** Ubuntu 22.04 LTS
- **ROS2:** Humble (installed via `install_ros2.sh`)
- **Compiler:** g++ 11+, cmake 3.22+

---

**Last updated:** April 2026 | DroneBooks
