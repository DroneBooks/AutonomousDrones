#!/usr/bin/env python3
"""
takeoff_land.py - Basic flight control (takeoff and landing)

This script demonstrates how to:
1. Connect to Ardupilot
2. Arm the drone
3. Take off to a specific altitude
4. Hold altitude for a set time
5. Land automatically

WARNING: This script WILL take off a physical drone.
Use it only in:
  - SITL simulation (no real hardware)
  - Open, safe area with supervision

Requirements:
    pip install dronekit

Usage:
    python3 takeoff_land.py --connect 127.0.0.1:14550 --alt 10

Parameters:
    --connect: Connection string (default: 127.0.0.1:14550)
    --alt:     Takeoff altitude in metres (default: 10)
    --time:    Hover time in seconds (default: 10)

Author: DroneAcademy.edu
License: MIT
"""

from dronekit import connect, VehicleMode, LocationGlobalRelative
import argparse
import time
import sys

def arm_and_takeoff(vehicle, altitude):
    """
    Arms the drone and takes off to the specified altitude.

    Args:
        vehicle:  Vehicle instance
        altitude: Target altitude in metres
    """
    print(f"\nPreparing for takeoff to {altitude}m...")

    while vehicle.is_armable is False:
        print("Waiting for drone to become armable...")
        time.sleep(1)

    print("✓ Drone ready to arm")

    print("Arming drone...")
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True

    while vehicle.armed is False:
        print("  Waiting for arm confirmation...")
        time.sleep(1)

    print("✓ Drone armed")

    print(f"Taking off to {altitude}m...")
    vehicle.simple_takeoff(altitude)

    while True:
        current_alt = vehicle.location.global_relative_frame.alt
        print(f"  Current altitude: {current_alt:.1f}m / {altitude}m")

        # Stop when 95% of target altitude is reached
        if current_alt >= altitude * 0.95:
            print(f"✓ Target altitude reached: {current_alt:.1f}m")
            break

        time.sleep(1)


def main():
    parser = argparse.ArgumentParser(description='Take off and land the drone')
    parser.add_argument('--connect', default='127.0.0.1:14550',
                        help='Connection string')
    parser.add_argument('--alt', type=float, default=10,
                        help='Takeoff altitude in metres (default: 10)')
    parser.add_argument('--time', type=int, default=10,
                        help='Hover time in seconds (default: 10)')

    args = parser.parse_args()

    print("="*60)
    print("TAKEOFF AND LAND")
    print("="*60)
    print(f"\nConnecting to: {args.connect}")

    try:
        vehicle = connect(args.connect, wait_ready=True)
        print("✓ Connected")

        print("\nSwitching to GUIDED mode...")
        vehicle.mode = VehicleMode("GUIDED")

        arm_and_takeoff(vehicle, args.alt)

        print(f"\nHovering for {args.time} seconds...")
        print("Watch Mission Planner/QGC to see real-time position")

        for i in range(args.time):
            alt = vehicle.location.global_relative_frame.alt
            print(f"  {i+1}s: Altitude={alt:.1f}m")
            time.sleep(1)

        print("\nLanding...")
        vehicle.mode = VehicleMode("LAND")

        while vehicle.location.global_relative_frame.alt > 0.1:
            alt = vehicle.location.global_relative_frame.alt
            print(f"  Altitude: {alt:.1f}m")
            time.sleep(1)

        print("✓ Landing complete")

        vehicle.armed = False
        print("✓ Drone disarmed")

        vehicle.close()
        print("✓ Disconnected")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
