#!/usr/bin/env python3
"""
change_mode.py - Change flight modes remotely

This script demonstrates how to:
1. Connect to Ardupilot
2. Read the current flight mode
3. Switch between different flight modes
4. Verify changes in QGroundControl

Available modes on Copter:
  - STABILIZE      (manual with stabilisation)
  - ALT_HOLD       (automatic altitude hold)
  - LOITER         (automatic position hold)
  - GUIDED         (waypoints via dronekit)
  - AUTO           (FC mission)
  - RTL            (return to launch)
  - LAND           (automatic landing)

Requirements:
    pip install dronekit

Usage:
    python3 change_mode.py --connect 127.0.0.1:14550

Author: DroneAcademy.edu
License: MIT
"""

from dronekit import connect, VehicleMode
import argparse
import time
import sys

def change_mode(vehicle, mode_name, duration=3):
    """
    Changes the drone flight mode and holds it for X seconds.

    Args:
        vehicle:   Vehicle instance
        mode_name: Mode name (e.g. "ALT_HOLD", "LOITER")
        duration:  Time in seconds to hold the mode
    """
    print(f"\nSwitching to mode: {mode_name}")
    print(f"Previous mode: {vehicle.mode.name}")

    vehicle.mode = VehicleMode(mode_name)

    # Wait for mode change confirmation
    timeout = time.time() + 10
    while vehicle.mode.name != mode_name:
        if time.time() > timeout:
            print(f"✗ Error: Could not switch to {mode_name}")
            return False
        print(f"  Waiting for confirmation... (current: {vehicle.mode.name})")
        time.sleep(0.5)

    print(f"✓ Current mode: {vehicle.mode.name}")

    print(f"  Holding {mode_name} for {duration}s...")
    for i in range(duration):
        alt = vehicle.location.global_relative_frame.alt
        print(f"    {i+1}s: {vehicle.mode.name} | Alt={alt:.1f}m")
        time.sleep(1)

    return True


def main():
    parser = argparse.ArgumentParser(description='Change flight modes remotely')
    parser.add_argument('--connect', default='127.0.0.1:14550',
                        help='Connection string')
    parser.add_argument('--time', type=int, default=3,
                        help='Time (seconds) in each mode (default: 3)')

    args = parser.parse_args()

    print("="*60)
    print("CHANGE FLIGHT MODE")
    print("="*60)
    print(f"\nConnecting to: {args.connect}")

    try:
        vehicle = connect(args.connect, wait_ready=True)
        print("✓ Connected")

        print(f"\nInitial mode: {vehicle.mode.name}")
        print("Watch QGroundControl to see changes in real time")
        print("-" * 60)

        # Mode sequence
        modes = [
            "STABILIZE",     # Full manual with stabilisation
            "ALT_HOLD",      # Holds altitude automatically
            "LOITER",        # Holds position automatically
        ]

        for mode in modes:
            change_mode(vehicle, mode, duration=args.time)
            time.sleep(1)

        # Return to original mode
        print(f"\nReturning to mode: STABILIZE")
        change_mode(vehicle, "STABILIZE", duration=2)

        print("-" * 60)
        print("\n✓ Mode switching sequence completed")
        print("✓ Each transition should have been visible in QGC")

        vehicle.close()
        print("✓ Disconnected")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
