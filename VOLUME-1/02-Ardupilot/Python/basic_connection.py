#!/usr/bin/env python3
"""
basic_connection.py - Connect to Ardupilot and read basic telemetry

This script demonstrates how to:
1. Connect to an Ardupilot Flight Controller
2. Read telemetry data in real time
3. Display drone information

Requirements:
    pip install dronekit

Usage:
    python3 basic_connection.py --connect /dev/ttyUSB0   (Linux)
    python3 basic_connection.py --connect COM3             (Windows)
    python3 basic_connection.py --connect 127.0.0.1:14550 (SITL)

Author: DroneAcademy.edu
License: MIT
"""

from dronekit import connect, VehicleMode
import argparse
import time
import sys

def main():
    parser = argparse.ArgumentParser(description='Connect to Ardupilot and display telemetry')
    parser.add_argument('--connect', default='127.0.0.1:14550',
                        help='Connection string (serial port or IP:port)')
    parser.add_argument('--baudrate', type=int, default=57600,
                        help='Baud rate (default: 57600)')

    args = parser.parse_args()

    print("="*60)
    print("BASIC ARDUPILOT CONNECTION")
    print("="*60)
    print(f"\nConnecting to: {args.connect}")
    print("Waiting for telemetry...\n")

    try:
        vehicle = connect(args.connect, baud=args.baudrate, wait_ready=True)

        print("✓ Connected successfully!\n")

        print("VEHICLE INFORMATION:")
        print("-" * 60)
        print(f"Vehicle type: {vehicle.system_status.state}")
        print(f"Current mode: {vehicle.mode.name}")
        print(f"Armed: {'Yes' if vehicle.armed else 'No'}")
        print(f"Armable: {vehicle.is_armable}\n")

        print("LIVE TELEMETRY (10 seconds):")
        print("-" * 60)
        print(f"{'Time':<8} {'Altitude':<12} {'Airspeed':<12} {'Battery':<10} {'Satellites':<10}")
        print("-" * 60)

        start_time = time.time()
        while time.time() - start_time < 10:
            elapsed    = int(time.time() - start_time)
            altitude   = vehicle.location.global_relative_frame.alt or 0
            speed      = vehicle.airspeed or 0
            battery    = vehicle.battery.voltage or 0
            satellites = vehicle.gps_0.satellites_visible or 0

            print(f"{elapsed:<8} {altitude:<12.2f}m {speed:<12.2f}m/s {battery:<10.2f}V {satellites:<10}")

            time.sleep(1)

        print("-" * 60)
        print("\n✓ Telemetry read complete")

        vehicle.close()
        print("✓ Disconnected")

    except Exception as e:
        print(f"\n✗ Connection error: {e}")
        print("\nCheck:")
        print("  - FC connected via USB/telemetry radio")
        print("  - Correct serial port (COM3, /dev/ttyUSB0, etc.)")
        print("  - Correct baud rate (default: 57600)")
        print("  - SITL running on 127.0.0.1:14550")
        sys.exit(1)

if __name__ == '__main__':
    main()
