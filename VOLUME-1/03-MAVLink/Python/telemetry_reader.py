#!/usr/bin/env python3
"""
Volumen 1 — Capítulo 3: MAVLink — Lector de Telemetría en Tiempo Real
Lee GPS, actitud, batería y otros datos del FC continuamente
"""

import sys
import time
from pymavlink import mavutil
from datetime import datetime

class TelemetryReader:
    """Lector de telemetría MAVLink"""

    def __init__(self, connection_string: str):
        """Inicializa la conexión MAVLink"""
        self.mav = mavutil.mavlink_connection(connection_string, timeout=5)
        self.mav.wait_heartbeat(timeout=10)
        print(f"[OK] Conectado al autopiloto")

    def read_attitude(self) -> dict:
        """Lee datos de actitud (roll, pitch, yaw)"""
        msg = self.mav.recv_match(type='ATTITUDE', timeout=1)
        if msg:
            return {
                'time': msg.time_boot_ms,
                'roll': msg.roll,
                'pitch': msg.pitch,
                'yaw': msg.yaw,
                'rollspeed': msg.rollspeed,
                'pitchspeed': msg.pitchspeed,
                'yawspeed': msg.yawspeed
            }
        return None

    def read_gps(self) -> dict:
        """Lee datos de GPS"""
        msg = self.mav.recv_match(type='GPS_RAW_INT', timeout=1)
        if msg:
            return {
                'time_usec': msg.time_usec,
                'lat': msg.lat / 1e7,
                'lon': msg.lon / 1e7,
                'alt': msg.alt / 1000,  # mm a m
                'hdop': msg.eph / 100,
                'vdop': msg.epv / 100,
                'vel': msg.vel / 100,   # cm/s a m/s
                'cog': msg.cog / 100,   # centigrados a grados
                'satellites': msg.satellites_visible
            }
        return None

    def read_battery(self) -> dict:
        """Lee datos de batería"""
        msg = self.mav.recv_match(type='BATTERY_STATUS', timeout=1)
        if msg:
            return {
                'voltage': msg.voltage / 1000,  # mV a V
                'current': msg.current / 100,   # cA a A
                'remaining': msg.battery_remaining,
                'temperature': msg.temperature if hasattr(msg, 'temperature') else None
            }
        return None

    def read_status(self) -> dict:
        """Lee estado general del FC"""
        msg = self.mav.recv_match(type='SYS_STATUS', timeout=1)
        if msg:
            return {
                'voltage': msg.voltage_battery / 1000,
                'current': msg.current_battery / 100,
                'battery': msg.battery_remaining,
                'errors_comm': msg.errors_comm,
                'errors_count1': msg.errors_count1,
                'errors_count2': msg.errors_count2,
                'errors_count3': msg.errors_count3,
                'errors_count4': msg.errors_count4
            }
        return None

    def print_telemetry(self, clear: bool = False):
        """Imprime telemetría formateada"""
        if clear:
            print("\033[H\033[J", end="")  # Limpia pantalla (Linux)

        timestamp = datetime.now().strftime("%H:%M:%S")

        print(f"\n{'='*70}")
        print(f"TELEMETRÍA - {timestamp}")
        print(f"{'='*70}")

        # Actitud
        attitude = self.read_attitude()
        if attitude:
            print(f"\n[ACTITUD]")
            print(f"  Roll:       {attitude['roll']:7.2f} rad  ({attitude['roll']*180/3.14159:7.2f}°)")
            print(f"  Pitch:      {attitude['pitch']:7.2f} rad  ({attitude['pitch']*180/3.14159:7.2f}°)")
            print(f"  Yaw:        {attitude['yaw']:7.2f} rad  ({attitude['yaw']*180/3.14159:7.2f}°)")
            print(f"  RollRate:   {attitude['rollspeed']:7.2f} rad/s")
            print(f"  PitchRate:  {attitude['pitchspeed']:7.2f} rad/s")
            print(f"  YawRate:    {attitude['yawspeed']:7.2f} rad/s")

        # GPS
        gps = self.read_gps()
        if gps:
            print(f"\n[GPS]")
            print(f"  Latitud:    {gps['lat']:12.6f}°")
            print(f"  Longitud:   {gps['lon']:12.6f}°")
            print(f"  Altitud:    {gps['alt']:10.2f} m")
            print(f"  Velocidad:  {gps['vel']:10.2f} m/s")
            print(f"  HDOP:       {gps['hdop']:10.2f} (precisión horizontal)")
            print(f"  Satélites:  {gps['satellites']:3d}")

        # Batería
        battery = self.read_battery()
        if battery:
            print(f"\n[BATERÍA]")
            print(f"  Voltaje:    {battery['voltage']:6.2f} V")
            print(f"  Corriente:  {battery['current']:6.2f} A")
            print(f"  Restante:   {battery['remaining']:3d} %")
            if battery['temperature'] is not None:
                print(f"  Temperatura: {battery['temperature']:3d} °C")

        # Estado del sistema
        status = self.read_status()
        if status:
            print(f"\n[ESTADO DEL SISTEMA]")
            print(f"  Errores COM: {status['errors_comm']}")

        print(f"{'='*70}\n")

    def run_continuous(self, duration: int = 60, interval: float = 1.0):
        """Ejecuta lectura continua de telemetría"""
        print(f"\n[*] Leyendo telemetría durante {duration} segundos...")
        print(f"[*] Intervalo: {interval} segundos")

        start_time = time.time()

        try:
            while time.time() - start_time < duration:
                self.print_telemetry(clear=False)
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n[*] Interrumpido por usuario")
        finally:
            self.mav.close()
            print("[OK] Conexión cerrada")

def main():
    """Función principal"""
    connection_string = '127.0.0.1:14550'  # SITL por defecto

    if len(sys.argv) > 1:
        connection_string = sys.argv[1]

    print("=" * 70)
    print("Volumen 1 — Capítulo 3: MAVLink — Lector de Telemetría")
    print("=" * 70)

    try:
        reader = TelemetryReader(connection_string)
        reader.run_continuous(duration=300, interval=2.0)
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
