#!/usr/bin/env python3
"""Simple ROS2 subscriber node — Chapter 4: ROS2.

Subscribes to topic 'message' and logs each received message.
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class MySubscriber(Node):
    def __init__(self):
        super().__init__('my_subscriber')

        # Subscribe to topic 'message'
        self.subscription = self.create_subscription(
            String,
            'message',
            self.listener_callback,
            10  # Queue depth
        )
        self.subscription  # Prevent warning

    def listener_callback(self, msg):
        """Called when a new message arrives"""
        self.get_logger().info(f'Received: {msg.data}')


def main(args=None):
    rclpy.init(args=args)
    node = MySubscriber()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
