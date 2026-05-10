#!/usr/bin/env python3
"""Simple ROS2 publisher node — Chapter 4: ROS2.

Publishes a text message on topic 'message' every second.
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class MyPublisher(Node):
    def __init__(self):
        super().__init__('my_publisher')

        # Create publisher on topic 'message'
        self.publisher_ = self.create_publisher(
            String,
            'message',  # Topic name
            10          # Queue depth
        )

        # Create timer to send every 1 second
        self.timer_period = 1.0
        self.timer = self.create_timer(
            self.timer_period,
            self.timer_callback
        )

        # Counter for demonstration
        self.counter = 0

    def timer_callback(self):
        """Function called every 1 second"""
        msg = String()
        msg.data = f'Message #{self.counter}'

        # Publish message
        self.publisher_.publish(msg)

        # Log
        self.get_logger().info(f'Publishing: {msg.data}')

        self.counter += 1


def main(args=None):
    # Initialise ROS2
    rclpy.init(args=args)

    # Create node
    node = MyPublisher()

    # Keep running
    rclpy.spin(node)

    # Cleanup
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
