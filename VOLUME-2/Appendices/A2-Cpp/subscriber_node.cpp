/*
 * subscriber_node.cpp — ROS2 drone telemetry subscriber node
 *
 * Example ROS2 C++ node that:
 * 1. Subscribes to telemetry topics
 * 2. Receives messages and processes them in callbacks
 * 3. Implements simple control logic
 *
 * Build:
 *   cd ~/ros2_ws && colcon build --packages-select drone_telemetry
 *
 * Run (start publisher_node in another terminal first):
 *   source install/setup.bash
 *   ros2 run drone_telemetry subscriber_node
 *
 * Key concepts (from Appendix A2):
 * - Subscription with create_subscription<T>
 * - Callbacks (std::function) that process messages
 * - const references to avoid unnecessary copies
 * - Control logic based on incoming data
 */

#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/float64.hpp"

class TelemetrySubscriberNode : public rclcpp::Node {
public:
    TelemetrySubscriberNode() : Node("telemetry_subscriber"),
                                 current_altitude_(0.0),
                                 current_battery_(100.0),
                                 current_speed_(0.0) {
        /*
         * Subscribe to telemetry topics.
         * Parameter 10: queue size (max pending messages).
         *
         * Use std::bind to link the callback method to the instance.
         * Signature: void callback(const std_msgs::msg::Float64::SharedPtr msg)
         */
        sub_altitude_ = create_subscription<std_msgs::msg::Float64>(
            "/telemetry/altitude", 10,
            std::bind(&TelemetrySubscriberNode::altitude_callback, this,
                      std::placeholders::_1));

        sub_battery_ = create_subscription<std_msgs::msg::Float64>(
            "/telemetry/battery", 10,
            std::bind(&TelemetrySubscriberNode::battery_callback, this,
                      std::placeholders::_1));

        sub_speed_ = create_subscription<std_msgs::msg::Float64>(
            "/telemetry/speed", 10,
            std::bind(&TelemetrySubscriberNode::speed_callback, this,
                      std::placeholders::_1));

        RCLCPP_INFO(get_logger(),
                    "✅ Subscriber node started — listening on /telemetry/*");
    }

private:
    /*
     * Altitude callback.
     * Fires EVERY TIME a message arrives on /telemetry/altitude.
     *
     * const auto&: const reference (avoids unnecessary copy).
     * SharedPtr:   smart pointer (RAII, auto-destruction).
     */
    void altitude_callback(const std_msgs::msg::Float64::SharedPtr msg) {
        current_altitude_ = msg->data;

        // Control logic: warn if altitude is dangerously low
        if (current_altitude_ < 2.0) {
            RCLCPP_WARN(get_logger(),
                        "⚠️  WARNING: Very low altitude: %.2f m", current_altitude_);
        }
    }

    /*
     * Battery callback.
     * Logic: alert if battery is critically low (< 15%).
     */
    void battery_callback(const std_msgs::msg::Float64::SharedPtr msg) {
        current_battery_ = msg->data;

        if (current_battery_ < 15.0) {
            RCLCPP_ERROR(
                get_logger(),
                "🔴 CRITICAL: Battery very low: %.1f%% — RETURN TO HOME",
                current_battery_);
        } else if (current_battery_ < 30.0) {
            RCLCPP_WARN(get_logger(),
                        "🟠 WARNING: Low battery: %.1f%%", current_battery_);
        }
    }

    /*
     * Speed callback.
     * Implements a maximum speed limit check.
     */
    void speed_callback(const std_msgs::msg::Float64::SharedPtr msg) {
        current_speed_ = msg->data;

        const double MAX_SPEED = 15.0;  // m/s
        if (current_speed_ > MAX_SPEED) {
            RCLCPP_WARN(get_logger(),
                        "⚠️  Speed exceeds limit: %.2f m/s (max: %.1f)",
                        current_speed_, MAX_SPEED);
        }
    }

public:
    /*
     * Getters to access current data (useful in other nodes).
     * Note: in multi-threading, these would need a mutex for safety.
     */
    double get_altitude() const { return current_altitude_; }
    double get_battery()  const { return current_battery_;  }
    double get_speed()    const { return current_speed_;    }

    /*
     * Example method: decision logic based on telemetry.
     * Returns true if the drone is safe to fly.
     */
    bool is_safe_to_fly() const {
        return (current_battery_  > 20.0) &&  // Sufficient battery
               (current_altitude_ >= 0.5);    // Not on the ground
    }

private:
    // Subscribers
    rclcpp::Subscription<std_msgs::msg::Float64>::SharedPtr sub_altitude_;
    rclcpp::Subscription<std_msgs::msg::Float64>::SharedPtr sub_battery_;
    rclcpp::Subscription<std_msgs::msg::Float64>::SharedPtr sub_speed_;

    // Member variables: current state
    double current_altitude_;
    double current_battery_;
    double current_speed_;
};

int main(int argc, char* argv[]) {
    rclcpp::init(argc, argv);
    auto node = std::make_shared<TelemetrySubscriberNode>();
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}
