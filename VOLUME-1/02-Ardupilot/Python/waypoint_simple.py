#!/usr/bin/env python3
"""
waypoint_simple.py - Crear y ejecutar una misión simple con waypoints

Este script demuestra cómo:
1. Crear una misión con 4 waypoints en forma de cuadrado
2. Enviar la misión a Ardupilot
3. Cambiar a modo AUTO
4. Monitorear la ejecución

Los waypoints se crean alrededor de la posición HOME actual.
La misión forma un cuadrado de 100m de lado.

Requisitos:
    pip install dronekit

Uso:
    python3 waypoint_simple.py --connect 127.0.0.1:14550

Autor: DroneAcademy.edu
Licencia: MIT
"""

from dronekit import connect, VehicleMode, LocationGlobalRelative
from pymavlink.dialects.v10 import mavutil
import argparse
import time
import sys

def create_waypoint(home_location, north, east, altitude):
    """
    Crea un waypoint offset desde HOME.

    Args:
        home_location: Ubicación HOME (LocationGlobal)
        north: Distancia norte en metros
        east: Distancia este en metros
        altitude: Altitud en metros

    Returns:
        LocationGlobalRelative con el waypoint
    """
    from math import cos, pi

    # Conversión aproximada (en la práctica usarías una librería de geodesia)
    lat_offset = north / 111000
    lon_offset = east / (111000 * cos(home_location.lat * pi / 180))

    return LocationGlobalRelative(
        home_location.lat + lat_offset,
        home_location.lon + lon_offset,
        altitude
    )


def create_mission():
    """
    Crea una misión simple: cuadrado de 100m con 4 waypoints.

    Returns:
        Lista de waypoints (LocationGlobalRelative)
    """
    # Estos waypoints son relativos a HOME (0,0)
    # Forman un cuadrado de 100m x 100m
    waypoints = [
        LocationGlobalRelative(0, 0, 25),      # WP1: Home (25m altura)
        LocationGlobalRelative(0, 100, 25),    # WP2: 100m Este
        LocationGlobalRelative(100, 100, 25),  # WP3: 100m Este, 100m Norte
        LocationGlobalRelative(100, 0, 25),    # WP4: 100m Norte
    ]
    return waypoints


def download_mission(vehicle):
    """
    Descarga la misión actual del FC.
    """
    missionlist = []
    m = vehicle.commands
    m.download()
    m.wait_ready()

    for cmd in m:
        missionlist.append(cmd)

    return missionlist


def upload_mission(vehicle, missionlist):
    """
    Sube una misión al FC.
    """
    m = vehicle.commands
    m.clear()

    for cmd in missionlist:
        m.add(cmd)

    m.upload()
    m.wait_ready()


def main():
    parser = argparse.ArgumentParser(description='Crea y ejecuta una misión simple')
    parser.add_argument('--connect', default='127.0.0.1:14550',
                        help='Cadena de conexión')
    parser.add_argument('--alt', type=float, default=25,
                        help='Altitud de misión en metros')

    args = parser.parse_args()

    print("="*60)
    print("MISIÓN SIMPLE CON WAYPOINTS")
    print("="*60)
    print(f"\nConectando a: {args.connect}")

    try:
        # Conectar
        vehicle = connect(args.connect, wait_ready=True)
        print("✓ Conectado")

        # Obtener ubicación HOME
        print("\nEsperando ubicación HOME (GPS)...")
        while vehicle.home_location is None:
            print("  Esperando GPS fix...")
            time.sleep(1)

        home_lat = vehicle.home_location.lat
        home_lon = vehicle.home_location.lon
        print(f"✓ HOME: ({home_lat}, {home_lon})")

        # Crear misión
        print("\nCreando misión (cuadrado 100m x 100m)...")
        cmds = vehicle.commands

        # Limpiar misión anterior
        cmds.clear()

        # Agregar comando de despegue
        cmds.add(mavutil.mavlink.MAVLink_mission_item_message(
            0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
            mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
            0, 1, 0, 0, 0, 0, 0, 0, args.alt))

        # Agregar waypoints
        wp_coords = [
            (0, 0),        # WP1: Home
            (0, 100),      # WP2: 100m Este
            (100, 100),    # WP3: 100m Este, 100m Norte
            (100, 0),      # WP4: 100m Norte
        ]

        for i, (north, east) in enumerate(wp_coords, 1):
            wp = create_waypoint(vehicle.home_location, north, east, args.alt)

            cmds.add(mavutil.mavlink.MAVLink_mission_item_message(
                0, i, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
                mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,
                0, 1, 0, 0, 0, 0, wp.lat, wp.lon, wp.alt))

            print(f"  WP{i}: ({north}m N, {east}m E, {args.alt}m Alt)")

        # Agregar comando de aterrizaje
        cmds.add(mavutil.mavlink.MAVLink_mission_item_message(
            0, len(wp_coords) + 1, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
            mavutil.mavlink.MAV_CMD_NAV_LAND,
            0, 1, 0, 0, 0, 0, home_lat, home_lon, 0))

        # Subir misión
        print("\nSubiendo misión a FC...")
        cmds.upload()
        time.sleep(1)

        print("✓ Misión cargada ({} waypoints)".format(len(wp_coords)))

        # Cambiar a modo AUTO
        print("\nCambiando a modo AUTO...")
        vehicle.mode = VehicleMode("AUTO")

        # Monitorear ejecución
        print("\nMonitoreando ejecución:")
        print("  Observa Mission Planner/QGC para ver el progreso en el mapa")
        print("-" * 60)

        while vehicle.mode.name == "AUTO":
            print(f"Altitud: {vehicle.location.global_relative_frame.alt:.1f}m | "
                  f"Velocidad: {vehicle.airspeed:.1f}m/s | "
                  f"Destino: WP{vehicle.commands.next + 1}")

            time.sleep(2)

        print("-" * 60)
        print("✓ Misión completada")

        vehicle.close()
        print("✓ Desconectado")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
