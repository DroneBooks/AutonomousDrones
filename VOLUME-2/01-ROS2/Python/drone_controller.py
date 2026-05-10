#!/usr/bin/env python3
"""Drone controller via ROS2 + MAVROS — Chapter 4: ROS2.

Subscribes to drone state and publishes position setpoints.
Switches to GUIDED mode and arms the drone after a brief delay.
"""

import rclpy
from rclpy.node import Node
from mavros_msgs.msg import State
from mavros_msgs.srv import CommandBool, SetMode
from geometry_msgs.msg import PoseStamped


class DroneController(Node):
    def __init__(self):
        super().__init__('drone_controller')

        # Subscribe to drone state
        self.state_sub = self.create_subscription(
            State,
            '/mavros/state',
            self.state_callback,
            10
        )

        # Target position publisher
        self.local_pos_pub = self.create_publisher(
            PoseStamped,
            '/mavros/setpoint_position/local',
            10
        )

        # Service clients
        self.arming_client = self.create_client(
            CommandBool,
            '/mavros/cmd/arming'
        )

        self.set_mode_client = self.create_client(
            SetMode,
            '/mavros/set_mode'
        )

        # State variables
        self.current_state = State()
        self.counter = 0

        # Timer to send commands
        self.timer = self.create_timer(0.1, self.timer_callback)

    def state_callback(self, msg):
        """Receives current drone state"""
        self.current_state = msg

        if msg.armed:
            self.get_logger().info('Drone ARMED')
        else:
            self.get_logger().info('Drone DISARMED')

    def timer_callback(self):
        """Sends target position"""
        if not self.current_state.connected:
            self.get_logger().warn('FC not connected')
            return

        # Create position target
        pose = PoseStamped()
        pose.header.stamp = self.get_clock().now().to_msg()
        pose.header.frame_id = 'map'
        pose.pose.position.x = 0.0
        pose.pose.position.y = 0.0
        pose.pose.position.z = 1.0  # 1 metre altitude

        self.local_pos_pub.publish(pose)

        # First attempt: switch to GUIDED mode
        if self.counter == 10:
            self.set_mode_request(0, 'GUIDED')

        # Second attempt: arm the drone
        if self.counter == 20:
            self.arm_drone()

        self.counter += 1

    def arm_drone(self):
        """Arms the drone"""
        request = CommandBool.Request()
        request.value = True

        future = self.arming_client.call_async(request)
        self.get_logger().info('Arming drone...')

    def set_mode_request(self, custom_mode, mode_name):
        """Changes flight mode"""
        request = SetMode.Request()
        request.custom_mode = mode_name

        future = self.set_mode_client.call_async(request)
        self.get_logger().info(f'Switching to mode: {mode_name}')


def main(args=None):
    rclpy.init(args=args)
    node = DroneController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
