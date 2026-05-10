#!/usr/bin/env python3
"""
Volumen 1 — Anexo A2: Python — Lectura Básica de Telemetría
Script simple para leer datos GPS, batería y actitud del drone
"""

from pymavlink import mavutil
import time

def main():
    """Función principal"""
    print("=" * 60)
    print("Volumen 1 — Anexo A2: Python — Lectura de Telemetría")
    print("=" * 60)

    # Conexión al Flight Controller
    # Para SITL (simulación): '127.0.0.1:14550'
    # Para serie real: '/dev/ttyUSB0' (Linux) o 'COM3' (Windows)

    connection_string = '127.0.0.1:14550'
    print(f"\n[*] Conectando a {connection_string}...")

    try:
        mav = mavutil.mavlink_connection(connection_string, timeout=5)
        mav.wait_heartbeat(timeout=10)
        print("[OK] ¡Conectado!")
    except Exception as e:
        print(f"[ERROR] No se pudo conectar: {e}")
        return

    # Leer telemetría durante 30 segundos
    print("\n[*] Leyendo telemetría durante 30 segundos...\n")

    start_time = time.time()

    while time.time() - start_time < 30:
        # Leer datos GPS
        msg_gps = mav.recv_match(type='GPS_RAW_INT', timeout=1)
        if msg_gps:
            lat = msg_gps.lat / 1e7
            lon = msg_gps.lon / 1e7
            alt = msg_gps.alt / 1000  # Convertir mm a metros
            print(f"GPS: Lat={lat:.6f}, Lon={lon:.6f}, Alt={alt:.2f}m")

        # Leer datos de batería
        msg_battery = mav.recv_match(type='BATTERY_STATUS', timeout=1)
        if msg_battery:
            voltage = msg_battery.voltage / 1000  # Convertir mV a V
            current = msg_battery.current / 100   # Convertir cA a A
            remaining = msg_battery.battery_remaining
            print(f"Batería: {voltage:.2f}V, {current:.2f}A, {remaining}% restante")

        # Leer datos de actitud
        msg_attitude = mav.recv_match(type='ATTITUDE', timeout=1)
        if msg_attitude:
            roll = msg_attitude.roll * 180 / 3.14159
            pitch = msg_attitude.pitch * 180 / 3.14159
            yaw = msg_attitude.yaw * 180 / 3.14159
            print(f"Actitud: Roll={roll:.1f}°, Pitch={pitch:.1f}°, Yaw={yaw:.1f}°")

        time.sleep(1)

    # Cerrar conexión
    mav.close()
    print("\n[OK] Conexión cerrada")

if __name__ == "__main__":
    main()
