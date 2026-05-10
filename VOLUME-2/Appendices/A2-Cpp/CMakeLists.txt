# CMakeLists.txt — Build template for ROS2 C++ nodes
#
# Configures the build of ROS2 nodes using CMake and colcon.
#
# Key concepts (from Appendix A2):
# - cmake_minimum_required: minimum CMake version
# - project(): package name and version
# - find_package(): locate installed dependencies
# - add_executable(): compile .cpp file into executable
# - ament_target_dependencies(): link ROS2 dependencies
# - install(): copy executables to install/lib/
# - ament_package(): finalise package definition
#
# Build:
#   cd ~/ros2_ws
#   colcon build --packages-select drone_telemetry
#
# Clean rebuild (if there are errors):
#   rm -rf build/ install/ log/
#   colcon build --packages-select drone_telemetry

cmake_minimum_required(VERSION 3.16)
project(drone_telemetry)

# C++ standard (14 minimum for ROS2, 17 recommended for modern features)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Locate ROS2 dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)

# ============================================================
# NODE 1: Telemetry Publisher
# ============================================================
# Compile publisher_node.cpp into the "publisher_node" executable
add_executable(publisher_node src/publisher_node.cpp)

# Link required ROS2 dependencies
ament_target_dependencies(publisher_node
  rclcpp
  std_msgs
)

# ============================================================
# NODE 2: Telemetry Subscriber
# ============================================================
add_executable(subscriber_node src/subscriber_node.cpp)

ament_target_dependencies(subscriber_node
  rclcpp
  std_msgs
)

# ============================================================
# NODE 3: MAVLink Bridge (optional, if bridge_mavlink.cpp exists)
# ============================================================
# Uncomment when bridge_mavlink.cpp is implemented
# find_package(pymavlink REQUIRED)
# add_executable(bridge_mavlink src/bridge_mavlink.cpp)
# ament_target_dependencies(bridge_mavlink rclcpp std_msgs pymavlink)

# ============================================================
# Installation
# ============================================================
# Copy compiled executables to install/lib/drone_telemetry/
install(TARGETS
  publisher_node
  subscriber_node
  DESTINATION lib/${PROJECT_NAME}
)

# Optional: copy configuration or launch files
# install(DIRECTORY config/ DESTINATION share/${PROJECT_NAME}/config)
# install(DIRECTORY launch/ DESTINATION share/${PROJECT_NAME}/launch)

# Finalise package definition (MUST be the last command)
ament_package()

# ============================================================
# Quick build reference
# ============================================================
# Build only this package:
#   colcon build --packages-select drone_telemetry
#
# Build with verbose output:
#   colcon build --packages-select drone_telemetry --cmake-args -DCMAKE_BUILD_TYPE=RelWithDebInfo
#
# Run after building:
#   source install/setup.bash
#   ros2 run drone_telemetry publisher_node
#   # (in another terminal)
#   ros2 run drone_telemetry subscriber_node
