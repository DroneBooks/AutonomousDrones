#!/usr/bin/env python3
"""
Volumen 1 — Capítulo 2: Ardupilot — Configurador de Parámetros
Lee y modifica parámetros del Flight Controller vía MAVLink
"""

import sys
from pymavlink import mavutil
import time

class ParameterConfigurator:
    """Gestor de parámetros de Ardupilot"""

    def __init__(self, connection_string):
        """Conecta al FC"""
        print(f"[*] Conectando a {connection_string}...")
        self.mav = mavutil.mavlink_connection(connection_string, timeout=5)
        self.mav.wait_heartbeat(timeout=10)
        print("[OK] Conectado al FC")

        self.common_params = {
            'SERIAL1_BAUD': (57600, 'Baudrate Serial 1'),
            'FRAME': (3, 'Tipo de frame (3=Quadcopter X)'),
            'LOG_BITMASK': (176, 'Qué registrar en logs'),
            'ARMING_CHECK': (1, 'Verificaciones de armado (1=todas)'),
            'FS_EKF_ACTION': (1, 'Acción en fallo EKF'),
            'FS_THR_ENABLE': (1, 'Failsafe de throttle'),
            'FS_THR_VALUE': (975, 'Valor throttle failsafe'),
            'RC_MIN': (1100, 'RC mínimo'),
            'RC_MAX': (1900, 'RC máximo'),
            'RC_TRIM': (1500, 'RC neutro'),
        }

    def read_parameter(self, param_name):
        """Lee un parámetro del FC"""
        print(f"[*] Leyendo parámetro {param_name}...")

        self.mav.param_fetch_all()
        start = time.time()

        while time.time() - start < 10:
            msg = self.mav.recv_match(type='PARAM_VALUE', blocking=False)
            if msg and msg.param_id.decode().rstrip('\x00') == param_name:
                return msg.param_value
            time.sleep(0.1)

        print(f"[!] Parámetro {param_name} no encontrado o timeout")
        return None

    def write_parameter(self, param_name, value):
        """Escribe un parámetro en el FC"""
        print(f"[*] Escribiendo {param_name} = {value}...")

        self.mav.param_set_message(param_name, value)

        # Esperar confirmación
        start = time.time()
        while time.time() - start < 10:
            msg = self.mav.recv_match(type='PARAM_VALUE', blocking=False)
            if msg and msg.param_id.decode().rstrip('\x00') == param_name:
                if msg.param_value == value:
                    print(f"[OK] {param_name} = {value}")
                    return True
                else:
                    print(f"[ERROR] Valor no confirmado")
                    return False
            time.sleep(0.1)

        print(f"[!] Timeout esperando confirmación")
        return False

    def show_menu(self):
        """Muestra menú de opciones"""
        print("\n" + "="*70)
        print("CONFIGURADOR DE PARÁMETROS - Ardupilot")
        print("="*70)
        print("""
[1] Leer parámetro específico
[2] Escribir parámetro específico
[3] Mostrar parámetros comunes
[4] Configurar parámetros básicos recomendados
[5] Salir
        """)

    def show_common_params(self):
        """Muestra parámetros comunes y sus valores"""
        print("\nPARÁMETROS COMUNES DE ARDUPILOT:")
        print("-" * 70)

        for param_name, (default_val, description) in self.common_params.items():
            current_val = self.read_parameter(param_name)
            if current_val is not None:
                print(f"{param_name:20} = {current_val:10.1f}  ({description})")
            else:
                print(f"{param_name:20} = [NO ENCONTRADO]  ({description})")

        print("-" * 70)

    def configure_basic(self):
        """Configura parámetros básicos recomendados"""
        print("\n[*] Configurando parámetros básicos recomendados...")

        configs = [
            ('ARMING_CHECK', 1, 'Verificaciones de armado activas'),
            ('LOG_BITMASK', 176, 'Logging básico'),
            ('FS_THR_ENABLE', 1, 'Failsafe de throttle activo'),
            ('SERIAL1_BAUD', 57600, 'Velocidad serial de telemetría'),
        ]

        for param_name, value, description in configs:
            print(f"\n{description}")
            self.write_parameter(param_name, value)

        print("\n[OK] Configuración básica completada")

    def run_interactive(self):
        """Ejecuta menú interactivo"""

        while True:
            self.show_menu()
            choice = input("Selecciona opción: ").strip()

            if choice == '1':
                param_name = input("Nombre del parámetro: ").strip().upper()
                value = self.read_parameter(param_name)
                if value is not None:
                    print(f"[OK] {param_name} = {value}")

            elif choice == '2':
                param_name = input("Nombre del parámetro: ").strip().upper()
                try:
                    value = float(input("Nuevo valor: "))
                    confirm = input(f"¿Escribir {param_name} = {value}? (s/n): ").strip().lower()
                    if confirm == 's':
                        self.write_parameter(param_name, value)
                except ValueError:
                    print("[ERROR] Valor no válido")

            elif choice == '3':
                self.show_common_params()

            elif choice == '4':
                confirm = input("¿Aplicar configuración básica? (s/n): ").strip().lower()
                if confirm == 's':
                    self.configure_basic()

            elif choice == '5':
                print("[*] Saliendo...")
                break

            else:
                print("[!] Opción no válida")

    def close(self):
        """Cierra la conexión"""
        self.mav.close()
        print("[OK] Conexión cerrada")

def main():
    """Función principal"""
    connection_string = '127.0.0.1:14550'  # SITL por defecto

    if len(sys.argv) > 1:
        connection_string = sys.argv[1]

    print("="*70)
    print("Volumen 1 — Capítulo 2: Ardupilot — Configurador de Parámetros")
    print("="*70)

    try:
        configurator = ParameterConfigurator(connection_string)
        configurator.run_interactive()
        configurator.close()
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
