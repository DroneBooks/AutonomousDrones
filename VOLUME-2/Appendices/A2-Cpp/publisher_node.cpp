/*
 * publisher_node.cpp — ROS2 drone telemetry publisher node
 *
 * Minimal ROS2 C++ node example that:
 * 1. Publishes telemetry data (altitude, speed, battery)
 * 2. Uses a timer to publish periodically (every 500 ms)
 * 3. Demonstrates essential C++ syntax for ROS2
 *
 * Build:
 *   cd ~/ros2_ws && colcon build --packages-select drone_telemetry
 *
 * Run:
 *   source install/setup.bash
 *   ros2 run drone_telemetry publisher_node
 *
 * Listen in another terminal:
 *   ros2 topic echo /telemetry/altitude
 *   ros2 topic echo /telemetry/battery
 *   ros2 topic echo /telemetry/speed
 *
 * Key concepts (from Appendix A2):
 * - Class inheriting from rclcpp::Node
 * - Publisher<T> for sending typed messages
 * - Periodic timer with std::bind
 * - Logging with RCLCPP_INFO
 */

#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/float64.hpp"
#include <cmath>

class TelemetryPublisherNode : public rclcpp::Node {
public:
    TelemetryPublisherNode() : Node("telemetry_publisher"), counter_(0) {
        /*
         * Create publishers for three topics:
         * - /telemetry/altitude   (metres)
         * - /telemetry/battery    (percentage 0-100)
         * - /telemetry/speed      (m/s)
         *
         * Parameter 10: history buffer (queue size)
         */
        pub_altitude_ = create_publisher<std_msgs::msg::Float64>(
            "/telemetry/altitude", 10);
        pub_battery_  = create_publisher<std_msgs::msg::Float64>(
            "/telemetry/battery", 10);
        pub_speed_    = create_publisher<std_msgs::msg::Float64>(
            "/telemetry/speed", 10);

        /*
         * Periodic timer: fires callback every 500 ms.
         * std::bind binds the method to the class instance.
         */
        timer_ = create_wall_timer(
            std::chrono::milliseconds(500),
            std::bind(&TelemetryPublisherNode::publish_callback, this));

        RCLCPP_INFO(get_logger(),
                    "✅ Publisher node started — topics: /telemetry/*");
    }

private:
    void publish_callback() {
        /*
         * Simulate varying telemetry (in production: read from Pixhawk).
         * Patterns: altitude rises and falls, battery decreases, speed oscillates.
         */
        counter_++;

        // Simulate varying altitude (0-30 metres, sinusoidal pattern)
        double altitude = 10.0 + 8.0 * std::sin(counter_ * 0.1);

        // Simulate battery (starts at 100%, decreases slowly)
        double battery  = 100.0 - (counter_ * 0.1);
        battery = (battery < 0) ? 0 : battery;

        // Simulate speed (0-5 m/s, triangular pattern)
        double speed = 2.5 + 1.5 * std::sin(counter_ * 0.05);

        // Create messages
        auto msg_alt = std_msgs::msg::Float64();
        msg_alt.data = altitude;

        auto msg_bat = std_msgs::msg::Float64();
        msg_bat.data = battery;

        auto msg_spd = std_msgs::msg::Float64();
        msg_spd.data = speed;

        // Publish
        pub_altitude_->publish(msg_alt);
        pub_battery_->publish(msg_bat);
        pub_speed_->publish(msg_spd);

        // Log every 4 cycles (every 2 seconds)
        if (counter_ % 4 == 0) {
            RCLCPP_INFO(
                get_logger(),
                "📡 Altitude: %.2f m | Battery: %.1f%% | Speed: %.2f m/s",
                altitude, battery, speed);
        }
    }

    // Private members
    rclcpp::Publisher<std_msgs::msg::Float64>::SharedPtr pub_altitude_;
    rclcpp::Publisher<std_msgs::msg::Float64>::SharedPtr pub_battery_;
    rclcpp::Publisher<std_msgs::msg::Float64>::SharedPtr pub_speed_;
    rclcpp::TimerBase::SharedPtr timer_;
    int counter_;
};

int main(int argc, char* argv[]) {
    /*
     * Initialise ROS2: must be the first call.
     * Arguments: argc, argv (allows passing parameters from the command line).
     */
    rclcpp::init(argc, argv);

    /*
     * Create node instance and pass it to spin().
     * spin() blocks until shutdown is signalled.
     * std::make_shared: creates a shared pointer (C++11 pattern).
     */
    auto node = std::make_shared<TelemetryPublisherNode>();
    rclcpp::spin(node);

    /* Shutdown: frees resources and stops the node. */
    rclcpp::shutdown();
    return 0;
}
