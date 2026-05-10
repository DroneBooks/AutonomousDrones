#!/usr/bin/env python3
"""
geofence_define.py - Define virtual boundaries (geofence) for the drone

This script demonstrates how to:
1. Define a virtual boundary (geofence)
2. Configure geofence parameters on the FC
3. Verify that the drone respects limits in QGroundControl

The geofence is a virtual perimeter. If the drone tries to leave:
  - LOITER mode: Returns to boundary automatically
  - GUIDED mode: Stops movement
  - All modes: Activates failsafe if configured

Requirements:
    pip install dronekit pymavlink

Usage:
    python3 geofence_define.py --connect 127.0.0.1:14550

Key parameters:
    FENCE_ENABLE=1            (enable geofence)
    FENCE_TYPE=1              (1=circle, 2=polygon)
    FENCE_RADIUS=100          (radius in metres for circle type)
    FENCE_ACTION=1            (0=report, 1=loiter, 2=guided, 3=rtl)

Author: DroneAcademy.edu
License: MIT
"""

from dronekit import connect
from pymavlink.dialects.v10 import mavutil
import argparse
import time
import sys

def read_parameter(vehicle, name):
    """Reads a parameter from the FC."""
    vehicle.parameters[name]
    return vehicle.parameters.get(name)


def set_parameter(vehicle, name, value):
    """Sets a parameter on the FC."""
    print(f"  Setting {name} = {value}")
    vehicle.parameters[name] = value

    # Wait for confirmation
    timeout = time.time() + 5
    while vehicle.parameters[name] != value:
        if time.time() > timeout:
            print(f"    ✗ Timeout setting {name}")
            return False
        time.sleep(0.1)

    print(f"    ✓ {name} confirmed")
    return True


def main():
    parser = argparse.ArgumentParser(description='Define geofence (virtual flight boundaries)')
    parser.add_argument('--connect', default='127.0.0.1:14550',
                        help='Connection string')
    parser.add_argument('--radius', type=float, default=100,
                        help='Geofence radius in metres (default: 100)')
    parser.add_argument('--type', type=int, default=1,
                        help='Type: 1=circle (default), 2=polygon')
    parser.add_argument('--action', type=int, default=1,
                        help='Action: 0=report, 1=loiter, 2=guided, 3=RTL')

    args = parser.parse_args()

    print("="*60)
    print("GEOFENCE (VIRTUAL FLIGHT BOUNDARIES)")
    print("="*60)
    print(f"\nConnecting to: {args.connect}")

    try:
        vehicle = connect(args.connect, wait_ready=True)
        print("✓ Connected")

        # Wait for HOME
        print("\nWaiting for HOME location (GPS)...")
        while vehicle.home_location is None:
            print("  Waiting for GPS fix...")
            time.sleep(1)

        home_lat = vehicle.home_location.lat
        home_lon = vehicle.home_location.lon
        print(f"✓ HOME: ({home_lat:.6f}, {home_lon:.6f})")

        # Read current parameters
        print("\nCurrent geofence parameters:")
        print("-" * 60)
        fence_enabled = read_parameter(vehicle, 'FENCE_ENABLE')
        fence_type    = read_parameter(vehicle, 'FENCE_TYPE')
        fence_radius  = read_parameter(vehicle, 'FENCE_RADIUS')
        fence_action  = read_parameter(vehicle, 'FENCE_ACTION')

        print(f"FENCE_ENABLE:  {fence_enabled} (0=disabled, 1=active)")
        print(f"FENCE_TYPE:    {fence_type} (1=circle, 2=polygon)")
        print(f"FENCE_RADIUS:  {fence_radius}m (for circle type)")
        print(f"FENCE_ACTION:  {fence_action} (0=report, 1=loiter, 2=guided, 3=RTL)")

        # Configure geofence
        print("\nConfiguring new geofence...")
        print("-" * 60)

        # Disable first
        set_parameter(vehicle, 'FENCE_ENABLE', 0)
        time.sleep(1)

        # Set parameters
        set_parameter(vehicle, 'FENCE_TYPE',   args.type)
        set_parameter(vehicle, 'FENCE_RADIUS', args.radius)
        set_parameter(vehicle, 'FENCE_ACTION', args.action)

        # Enable
        set_parameter(vehicle, 'FENCE_ENABLE', 1)

        print("\n✓ Geofence configured successfully")
        print(f"  - Radius: {args.radius}m from HOME")
        print(f"  - Action: ", end='')
        if args.action == 0:
            print("Report only")
        elif args.action == 1:
            print("Loiter (circle at boundary)")
        elif args.action == 2:
            print("Guided (stop movement)")
        else:
            print("RTL (return to home)")

        print("\n" + "="*60)
        print("VERIFICATION IN QGC")
        print("="*60)
        print("""
In QGroundControl, you should see:
1. A red circle on the map (centre = HOME, radius = {} metres)
2. The drone CANNOT exit this circle
3. If it tries to: {} action

To test:
1. Arm the drone
2. Switch to ALT_HOLD or LOITER
3. Try to fly it outside the circle with RC
4. Watch the drone stop/loiter at the boundary
5. Logs will show "FENCE_BREACH" messages
""".format(args.radius, ["report", "loiter", "stop", "RTL"][args.action]))

        # Monitor for 30 seconds
        print("Monitoring geofence status (30 seconds)...")
        print("-" * 60)

        start_time = time.time()
        while time.time() - start_time < 30:
            elapsed      = int(time.time() - start_time)
            fence_enabled = read_parameter(vehicle, 'FENCE_ENABLE')
            fence_radius  = read_parameter(vehicle, 'FENCE_RADIUS')

            if vehicle.location.global_frame.lat is not None:
                # Very rough distance estimate
                lat_diff      = abs(vehicle.location.global_frame.lat - home_lat)
                lon_diff      = abs(vehicle.location.global_frame.lon - home_lon)
                approx_dist   = (lat_diff + lon_diff) * 111000  # metres, very approx

                status = "INSIDE" if approx_dist < args.radius else "OUTSIDE"
                print(f"{elapsed}s: Geofence={'ACTIVE' if fence_enabled else 'INACTIVE'} | "
                      f"Radius={fence_radius}m | Status={status}")
            else:
                print(f"{elapsed}s: Geofence={'ACTIVE' if fence_enabled else 'INACTIVE'} | "
                      f"Waiting for GPS...")

            time.sleep(2)

        print("-" * 60)
        print("✓ Monitoring complete")

        vehicle.close()
        print("✓ Disconnected")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
