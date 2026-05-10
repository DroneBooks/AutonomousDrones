#!/usr/bin/env python3
"""Flight status monitor — Chapter 4: ROS2.

Subscribes to four MAVROS topics simultaneously (state, GPS, battery, IMU)
and publishes a JSON summary on /drone/flight_status every 2 seconds.
"""

import json
from math import sqrt

import rclpy
from rclpy.node import Node
from mavros_msgs.msg import State
from sensor_msgs.msg import NavSatFix, BatteryState, Imu
from std_msgs.msg import String


class FlightStatusNode(Node):

    def __init__(self):
        super().__init__('flight_status')

        self._status = {
            'connected': False,
            'armed': False,
            'mode': 'UNKNOWN',
            'lat': 0.0,
            'lon': 0.0,
            'alt_m': 0.0,
            'battery_pct': 0.0,
            'battery_v': 0.0,
            'acceleration_m_s2': 0.0,
        }

        # Four MAVROS subscribers
        self.create_subscription(
            State, '/mavros/state', self._cb_state, 10)
        self.create_subscription(
            NavSatFix, '/mavros/global_position/global',
            self._cb_gps, 10)
        self.create_subscription(
            BatteryState, '/mavros/battery',
            self._cb_battery, 10)
        self.create_subscription(
            Imu, '/mavros/imu/data', self._cb_imu, 10)

        # JSON summary publisher
        self._pub = self.create_publisher(String,
        '/drone/flight_status', 10)

        # Publish every 2 seconds
        self.create_timer(2.0, self._publish_summary)
        self.get_logger().info('FlightStatus started...')

    def _cb_state(self, msg):
        self._status['connected'] = msg.connected
        self._status['armed']     = msg.armed
        self._status['mode']      = msg.mode

    def _cb_gps(self, msg):
        self._status['lat']   = round(msg.latitude, 6)
        self._status['lon']   = round(msg.longitude, 6)
        self._status['alt_m'] = round(msg.altitude, 1)

    def _cb_battery(self, msg):
        self._status['battery_v']   = round(msg.voltage, 2)
        pct = msg.percentage
        self._status['battery_pct'] = round(pct * 100, 1) \
        if pct == pct else -1.0

    def _cb_imu(self, msg):
        ax, ay, az = (msg.linear_acceleration.x,
                      msg.linear_acceleration.y,
                      msg.linear_acceleration.z)
        self._status['acceleration_m_s2'] = round(
            sqrt(ax**2 + ay**2 + az**2), 2)

    def _publish_summary(self):
        msg = String()
        msg.data = json.dumps(self._status, ensure_ascii=False)
        self._pub.publish(msg)

        s = self._status
        self.get_logger().info(
            f"{'ARMED' if s['armed'] else 'DISARMED'} | "
            f"Mode:{s['mode']} | Alt:{s['alt_m']}m | "
            f"Bat:{s['battery_pct']}%"
        )

        if s['battery_pct'] != -1.0 and s['battery_pct'] < 20.0:
            self.get_logger().warn(
                f"LOW BATTERY: {s['battery_pct']}%")


def main(args=None):
    rclpy.init(args=args)
    node = FlightStatusNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
