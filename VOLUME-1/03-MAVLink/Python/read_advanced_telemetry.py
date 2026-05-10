#!/usr/bin/env python3
"""
read_advanced_telemetry.py - Advanced telemetry reading with CSV export

This script demonstrates how to:
1. Read multiple telemetry data streams
2. Export data to a CSV file for later analysis
3. Calculate derived values (vertical speed, acceleration)
4. Generate a real-time report

Recorded data:
    - Position: Latitude, Longitude, Altitude (GPS)
    - Speed: Airspeed, vertical speed
    - Attitude: Roll, Pitch, Yaw
    - Battery: Voltage, Current, Percentage
    - System: Mode, Armed, GPS satellites

Requirements:
    pip install dronekit

Usage:
    python3 read_advanced_telemetry.py --connect 127.0.0.1:14550 --duration 30

Parameters:
    --connect:  Connection string (default: 127.0.0.1:14550)
    --duration: Recording time in seconds (default: 30)
    --file:     CSV output filename (default: telemetry.csv)

Output:
    - telemetry.csv: Tabulated data for analysis in Excel/Python
    - Statistics printed to console

Author: DroneAcademy.edu
License: MIT
"""

from dronekit import connect
import argparse
import time
import sys
import csv
import os

def main():
    parser = argparse.ArgumentParser(description='Read and record advanced telemetry')
    parser.add_argument('--connect', default='127.0.0.1:14550',
                        help='Connection string')
    parser.add_argument('--duration', type=int, default=30,
                        help='Recording duration in seconds (default: 30)')
    parser.add_argument('--file', default='telemetry.csv',
                        help='Output CSV file')

    args = parser.parse_args()

    print("="*60)
    print("ADVANCED TELEMETRY READER")
    print("="*60)
    print(f"\nConnecting to: {args.connect}")

    try:
        vehicle = connect(args.connect, wait_ready=True)
        print("✓ Connected")

        # Wait for HOME
        print("Waiting for HOME location...")
        while vehicle.home_location is None:
            print("  Waiting for GPS fix...")
            time.sleep(1)

        home_lat = vehicle.home_location.lat
        home_lon = vehicle.home_location.lon
        print(f"✓ HOME: ({home_lat:.6f}, {home_lon:.6f})")

        # Create CSV file
        print(f"\nRecording telemetry to: {args.file}")
        print("-" * 60)

        with open(args.file, 'w', newline='') as csvfile:
            fieldnames = [
                'time(s)', 'lat', 'lon', 'alt(m)', 'relative_altitude(m)',
                'airspeed(m/s)', 'vertical_speed(m/s)',
                'roll(deg)', 'pitch(deg)', 'yaw(deg)',
                'battery_voltage(V)', 'current(A)', 'battery_pct(%)',
                'mode', 'armed', 'gps_satellites', 'vdop'
            ]

            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            start_time   = time.time()
            prev_alt     = 0
            prev_time    = 0

            print(f"{'Time':<8} {'Alt':<8} {'Aspd':<8} {'Vspd':<8} "
                  f"{'Roll':<8} {'Pitch':<8} {'Yaw':<8} {'Battery':<10}")
            print("-" * 70)

            while time.time() - start_time < args.duration:
                elapsed      = time.time() - start_time
                current_time = elapsed

                try:
                    lat       = vehicle.location.global_frame.lat or 0
                    lon       = vehicle.location.global_frame.lon or 0
                    alt_gps   = vehicle.location.global_frame.alt or 0
                    alt_rel   = vehicle.location.global_relative_frame.alt or 0
                    airspeed  = vehicle.airspeed or 0

                    # Calculate vertical speed (altitude derivative)
                    if prev_time > 0:
                        delta_t       = current_time - prev_time
                        vertical_spd  = (alt_rel - prev_alt) / delta_t if delta_t > 0 else 0
                    else:
                        vertical_spd  = 0

                    # Attitude (convert radians to degrees)
                    roll  = vehicle.attitude.roll  * 180 / 3.14159
                    pitch = vehicle.attitude.pitch * 180 / 3.14159
                    yaw   = vehicle.attitude.yaw   * 180 / 3.14159

                    # Battery
                    voltage    = vehicle.battery.voltage or 0
                    current    = vehicle.battery.current or 0
                    battery_pct = vehicle.battery.level or 0

                    # System
                    mode       = vehicle.mode.name
                    armed      = 1 if vehicle.armed else 0
                    satellites = vehicle.gps_0.satellites_visible or 0
                    vdop       = vehicle.gps_0.vdop or 0

                    writer.writerow({
                        'time(s)':              f"{elapsed:.1f}",
                        'lat':                  f"{lat:.6f}",
                        'lon':                  f"{lon:.6f}",
                        'alt(m)':               f"{alt_gps:.1f}",
                        'relative_altitude(m)': f"{alt_rel:.1f}",
                        'airspeed(m/s)':        f"{airspeed:.1f}",
                        'vertical_speed(m/s)':  f"{vertical_spd:.1f}",
                        'roll(deg)':            f"{roll:.1f}",
                        'pitch(deg)':           f"{pitch:.1f}",
                        'yaw(deg)':             f"{yaw:.1f}",
                        'battery_voltage(V)':   f"{voltage:.2f}",
                        'current(A)':           f"{current:.1f}",
                        'battery_pct(%)':       f"{battery_pct:.0f}",
                        'mode':                 mode,
                        'armed':                armed,
                        'gps_satellites':       satellites,
                        'vdop':                 f"{vdop:.1f}"
                    })

                    print(f"{elapsed:<8.1f} {alt_rel:<8.1f} {airspeed:<8.1f} "
                          f"{vertical_spd:<8.2f} {roll:<8.1f} {pitch:<8.1f} "
                          f"{yaw:<8.1f} {voltage:.1f}V")

                    prev_alt  = alt_rel
                    prev_time = current_time

                except Exception as e:
                    print(f"  Error reading data: {e}")

                time.sleep(1)

        print("-" * 70)
        print(f"\n✓ File '{args.file}' created successfully")

        # Statistics
        print("\nCaptured statistics:")
        print("-" * 60)

        if os.path.exists(args.file):
            with open(args.file, 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                rows   = list(reader)

                if rows:
                    altitudes  = [float(r['relative_altitude(m)']) for r in rows]
                    voltages   = [float(r['battery_voltage(V)'])   for r in rows]
                    airspeeds  = [float(r['airspeed(m/s)'])        for r in rows]

                    print(f"Records captured   : {len(rows)}")
                    print(f"Duration           : {rows[-1]['time(s)']} seconds")
                    print(f"Altitude min/max/avg: {min(altitudes):.1f}m / "
                          f"{max(altitudes):.1f}m / {sum(altitudes)/len(altitudes):.1f}m")
                    print(f"Battery (min)      : {min(voltages):.2f}V")
                    print(f"Airspeed (max)     : {max(airspeeds):.1f}m/s")

        print("\n" + "="*60)
        print("Analysis:")
        print(f"  - Open {args.file} in Excel/Google Sheets for charts")
        print("  - Create plots: Altitude vs Time, Battery vs Time, etc.")
        print("  - Export for analysis in MATLAB/Python/R")

        vehicle.close()
        print("\n✓ Disconnected")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
