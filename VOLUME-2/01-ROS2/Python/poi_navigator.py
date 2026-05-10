#!/usr/bin/env python3
"""POI Navigator — Chapter 4: ROS2.

Navigates to a list of Points of Interest (POI) using Nav2.
Flies to each (x, y, z) coordinate sequentially.
"""

import rclpy
from rclpy.node import Node
from nav2_simple_commander.robot_navigator import BasicNavigator
from nav2_simple_commander.utils import getGoalFromUser
import geometry_msgs.msg as geometry_msgs
from rclpy.duration import Duration


class POINavigator(Node):
    def __init__(self):
        super().__init__('poi_navigator')
        self.navigator = BasicNavigator()

    def fly_to_point(self, x, y, z):
        """Flies to coordinate (x, y, z)"""

        # Wait until Nav2 is ready
        self.navigator.waitUntilNav2Active()
        self.get_logger().info('Nav2 active')

        # Create goal
        goal_pose = geometry_msgs.PoseStamped()
        goal_pose.header.frame_id = 'map'
        goal_pose.header.stamp = self.get_clock().now().to_msg()
        goal_pose.pose.position.x = float(x)
        goal_pose.pose.position.y = float(y)
        goal_pose.pose.position.z = float(z)
        goal_pose.pose.orientation.w = 1.0

        self.get_logger().info(
            f'Navigating to: ({x}, {y}, {z})'
        )

        # Send goal
        self.navigator.goToPose(goal_pose)

        # Monitor progress
        i = 0
        while not self.navigator.isTaskComplete():
            i += 1
            feedback = self.navigator.getFeedback()
            if feedback:
                self.get_logger().info(
                    f'Progress: {i} cycles, distance: '
                    f'{feedback.distance_remaining:.2f} m'
                )

            # Timeout: 30 seconds
            if Duration(seconds=i*0.1) > Duration(seconds=30):
                self.navigator.cancelTask()
                self.get_logger().warn('Timeout reached')
                break

        # Result
        result = self.navigator.getResult()
        if result:
            self.get_logger().info('Navigation completed OK')
        else:
            self.get_logger().error('Navigation failed')

    def fly_to_multiple_points(self, points):
        """Flies to multiple points sequentially.

        Args:
            points: List of tuples (x, y, z)
        """
        for i, (x, y, z) in enumerate(points):
            self.get_logger().info(
                f'Point {i+1}/{len(points)}'
            )
            self.fly_to_point(x, y, z)


def main(args=None):
    rclpy.init(args=args)
    node = POINavigator()

    # Define points of interest (POI)
    pois = [
        (10.0, 0.0, 5.0),    # POI 1
        (10.0, 10.0, 5.0),   # POI 2
        (0.0, 10.0, 5.0),    # POI 3
        (0.0, 0.0, 5.0),     # POI 4 (return to start)
    ]

    node.fly_to_multiple_points(pois)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
