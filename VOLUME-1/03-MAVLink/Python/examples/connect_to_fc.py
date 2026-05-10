#!/usr/bin/env python3
"""
Volumen 1 — Capítulo 3: MAVLink — Conexión Básica a Flight Controller
Demuestra cómo conectarse a un Ardupilot FC usando pymavlink
"""

import sys
import time
from pymavlink import mavutil

def connect_to_fc(connection_string: str, timeout: int = 30) -> mavutil.mavfile:
    """
    Conecta a un Flight Controller mediante MAVLink.

    Args:
        connection_string: Puerto de conexión (ej: '/dev/ttyUSB0', '127.0.0.1:14550')
        timeout: Tiempo máximo de espera en segundos

    Returns:
        Objeto mavutil.mavfile para comunicación
    """
    print(f"[*] Conectando a {connection_string}...")

    try:
        mav = mavutil.mavlink_connection(connection_string, timeout=timeout)
        mav.wait_heartbeat(timeout=timeout)
        print(f"[OK] Conexión establecida")
        print(f"[*] Autopiloto: {mav.autoinc_num}")
        return mav
    except Exception as e:
        print(f"[ERROR] No se pudo conectar: {e}")
        sys.exit(1)

def read_telemetry(mav: mavutil.mavfile, duration: int = 10):
    """
    Lee telemetría del FC durante N segundos.

    Args:
        mav: Conexión MAVLink
        duration: Duración en segundos
    """
    print(f"\n[*] Leyendo telemetría durante {duration} segundos...")
    print("-" * 60)

    start_time = time.time()

    while time.time() - start_time < duration:
        msg = mav.recv_match(type='ATTITUDE', timeout=1)

        if msg:
            print(f"[ATTITUDE]")
            print(f"  Roll:  {msg.roll:.2f} rad")
            print(f"  Pitch: {msg.pitch:.2f} rad")
            print(f"  Yaw:   {msg.yaw:.2f} rad")

        msg_gps = mav.recv_match(type='GPS_RAW_INT', timeout=1)
        if msg_gps:
            print(f"[GPS_RAW]")
            print(f"  Lat:  {msg_gps.lat / 1e7:.6f}")
            print(f"  Lon:  {msg_gps.lon / 1e7:.6f}")
            print(f"  Alt:  {msg_gps.alt / 1000:.2f} m")

        time.sleep(1)

    print("-" * 60)
    print("[OK] Lectura completada")

def main():
    """Función principal"""

    # Configuración de conexión
    # Para SITL: '127.0.0.1:14550'
    # Para serie real: '/dev/ttyUSB0' (Linux) o 'COM3' (Windows)
    connection_string = '127.0.0.1:14550'

    if len(sys.argv) > 1:
        connection_string = sys.argv[1]

    print("=" * 60)
    print("Volumen 1 — Capítulo 3: MAVLink — Conexión Básica")
    print("=" * 60)

    # Conectar al FC
    mav = connect_to_fc(connection_string, timeout=10)

    # Leer telemetría
    read_telemetry(mav, duration=10)

    # Cerrar conexión
    mav.close()
    print("\n[OK] Conexión cerrada")

if __name__ == "__main__":
    main()
