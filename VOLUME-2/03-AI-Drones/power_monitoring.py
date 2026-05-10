#!/usr/bin/env python3
"""
Monitoreo de consumo energético en tiempo real durante inferencia YOLO.

Este script mide el consumo de potencia en plataformas NVIDIA Jetson
mientras ejecuta inferencia con YOLO v8. Fundamental para diseño de
sistemas embarcados en drones con autonomía limitada.

Conceptos clave (del Capítulo 3 del libro):
    - Potencia = E/t (vatios = julios/segundo)
    - Autonomía en drones = capacidad_batería / potencia_media
    - IA embarcada consume menos que nube pero aún requiere energía

Uso:
    python power_monitoring.py --model yolov8n.pt
    python power_monitoring.py --model yolov8m.pt --interval 0.5
    python power_monitoring.py --model yolov8n.engine --duration 60
    python power_monitoring.py --model yolov8n.pt --export-csv power.csv

Nota importante:
    Este script está optimizado para NVIDIA Jetson (Nano/Orin).
    En otros sistemas, algunas métricas no estarán disponibles.

Requisitos (en Jetson):
    - pip install jetson-stats (para acceso a potencia)
    - pip install ultralytics opencv-python
"""

import argparse
import time
import csv
from pathlib import Path
from collections import deque
import subprocess
import numpy as np
import re

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    print("⚠️  Ultralytics no instalada. Instala con: pip install ultralytics")

try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    print("⚠️  OpenCV no instalado. Instala con: pip install opencv-python")

try:
    from jtop import jtop
    JTOP_AVAILABLE = True
except ImportError:
    JTOP_AVAILABLE = False
    print("⚠️  jetson-stats no instalado. Para Jetson: pip install jetson-stats")


class PowerMonitor:
    """Monitorea consumo de potencia durante inferencia YOLO."""

    def __init__(self, model_path, interval=1.0, max_duration=None):
        """
        Inicializa monitor de potencia.

        Args:
            model_path (str): Ruta del modelo YOLO
            interval (float): Intervalo de muestreo en segundos
            max_duration (float): Duración máxima en segundos (None = indefinido)
        """
        self.model_path = model_path
        self.interval = interval
        self.max_duration = max_duration

        # Cargar modelo
        if YOLO_AVAILABLE:
            self.model = YOLO(model_path)
        else:
            self.model = None

        # Historial de mediciones
        self.timestamps = []
        self.power_readings = []  # Watts
        self.gpu_load = []  # Porcentaje
        self.gpu_temp = []  # Celsius
        self.cpu_temp = []  # Celsius

        # Detectar plataforma
        self.is_jetson = self._detect_jetson()
        if not self.is_jetson:
            print("⚠️  No es Jetson. Usando mediciones estimadas.")

    def _detect_jetson(self):
        """Detecta si está corriendo en Jetson."""
        try:
            with open('/sys/firmware/devicetree/base/model', 'r') as f:
                model = f.read()
                return 'jetson' in model.lower()
        except:
            return False

    def _read_jetson_power(self):
        """Lee potencia de Jetson usando jtop."""
        if not JTOP_AVAILABLE:
            return None, None, None

        try:
            with jtop() as jetson:
                # Potencia en mW, convertir a W
                power_mw = jetson.power[0]['tot']  # 'tot' es potencia total
                power_w = power_mw / 1000.0

                gpu_load = jetson.gpu_load
                gpu_temp = jetson.temperature['GPU']

                return power_w, gpu_load, gpu_temp

        except Exception as e:
            print(f"⚠️  Error leyendo jtop: {e}")
            return None, None, None

    def _read_power_sysfs(self):
        """Lee potencia desde sysfs (fallback para Jetson sin jtop)."""
        try:
            # Jetson: /sys/devices/virtual/thermal/cooling_device*/cur_state
            # Alternativa: usar tegrastats
            result = subprocess.run(
                ['tegrastats', '--interval', '100'],
                capture_output=True,
                text=True,
                timeout=2
            )

            # Buscar "VDD_SYS" en salida
            match = re.search(r'VDD_SYS (\d+\.\d+)W', result.stdout)
            if match:
                return float(match.group(1))

        except:
            pass

        return None

    def _estimate_power_from_inference(self):
        """Estima potencia basada en actividad de inferencia."""
        # Estimación simple: baseline + overhead de inferencia
        # En CPU: ~5W baseline, +2W por inferencia
        # Con GPU: ~10W baseline, +5W por inferencia
        return 7.5  # Valor promedio estimado

    def read_power(self):
        """Lee potencia usando el mejor método disponible."""
        if self.is_jetson and JTOP_AVAILABLE:
            power, gpu_load, gpu_temp = self._read_jetson_power()
            if power is not None:
                return power, gpu_load, gpu_temp

        # Fallback
        power = self._estimate_power_from_inference()
        return power, None, None

    def monitoring_loop(self, num_frames=100):
        """
        Ejecuta loop de monitoreo mientras procesa frames.

        Args:
            num_frames (int): Número de frames a procesar
        """
        if self.model is None:
            print("❌ Modelo no cargado")
            return

        print(f"\n⚡ Iniciando monitoreo de potencia ({num_frames} frames)...")
        print("   Frame | Potencia (W) | GPU Load | GPU Temp | CPU Temp")
        print("   " + "-" * 60)

        # Imagen dummy para inferencia
        dummy_frame = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)

        start_time = time.time()

        for frame_idx in range(num_frames):
            # Registrar tiempo
            current_time = time.time() - start_time
            self.timestamps.append(current_time)

            # Leer potencia
            power, gpu_load, gpu_temp = self.read_power()

            # Ejecutar inferencia
            _ = self.model(dummy_frame, verbose=False)

            # Registrar
            if power is not None:
                self.power_readings.append(power)

            if gpu_load is not None:
                self.gpu_load.append(gpu_load)

            if gpu_temp is not None:
                self.gpu_temp.append(gpu_temp)

            # Mostrar progreso
            gpu_load_str = f"{gpu_load:.1f}%" if gpu_load is not None else "N/A"
            gpu_temp_str = f"{gpu_temp:.1f}°C" if gpu_temp is not None else "N/A"

            print(f"   {frame_idx + 1:3d}   | {power:11.2f} | {gpu_load_str:8} | "
                  f"{gpu_temp_str:8} | N/A")

            time.sleep(self.interval)

            # Verificar duración máxima
            if self.max_duration and current_time >= self.max_duration:
                print(f"   Duración máxima alcanzada ({self.max_duration}s)")
                break

        self.print_statistics()

    def print_statistics(self):
        """Imprime estadísticas de consumo energético."""
        if not self.power_readings:
            print("❌ No hay datos de potencia")
            return

        power = np.array(self.power_readings)
        duration = self.timestamps[-1] if self.timestamps else 0

        print("\n" + "="*70)
        print("⚡ ESTADÍSTICAS DE CONSUMO ENERGÉTICO")
        print("="*70)

        print(f"\n🔹 POTENCIA:")
        print(f"   Media:        {np.mean(power):.2f} W")
        print(f"   Mediana:      {np.median(power):.2f} W")
        print(f"   Min:          {np.min(power):.2f} W")
        print(f"   Max:          {np.max(power):.2f} W")
        print(f"   Desv. Est:    {np.std(power):.2f} W")

        # Energía consumida
        energy_wh = np.mean(power) * (duration / 3600)  # Wh
        energy_j = np.mean(power) * duration  # J

        print(f"\n🔹 ENERGÍA CONSUMIDA:")
        print(f"   Duración:     {duration:.2f} segundos")
        print(f"   Energía:      {energy_j:.2f} J ({energy_wh:.4f} Wh)")

        # Autonomía en drones (estimado)
        print(f"\n🔹 AUTONOMÍA EN DRONES (estimado):")
        battery_capacities = {
            'Mini (1000 mAh @ 7.7V)': 7.7,
            'Pequeño (2500 mAh @ 11.1V)': 27.75,
            'Mediano (5000 mAh @ 14.8V)': 74,
            'Grande (10000 mAh @ 14.8V)': 148,
        }

        power_inference = np.mean(power)
        power_base_drone = 5  # Estimación: otros sistemas del dron en W

        for battery_name, capacity_wh in battery_capacities.items():
            power_total = power_inference + power_base_drone
            autonomy_minutes = (capacity_wh / power_total) * 60
            print(f"   {battery_name:30} → {autonomy_minutes:.1f} min de IA activa")

        # Temperatura (si disponible)
        if self.gpu_temp:
            gpu_temp = np.array(self.gpu_temp)
            print(f"\n🔹 TEMPERATURA GPU:")
            print(f"   Media:        {np.mean(gpu_temp):.1f}°C")
            print(f"   Max:          {np.max(gpu_temp):.1f}°C")

            if np.max(gpu_temp) > 85:
                print(f"   ⚠️  ADVERTENCIA: Temperatura alta, riesgo de throttling")
            elif np.max(gpu_temp) > 70:
                print(f"   ⚠️  Temperatura elevada, monitorear disipación térmica")

        print("="*70)

    def export_csv(self, filepath):
        """Exporta datos a CSV."""
        if not self.power_readings:
            print("❌ No hay datos para exportar")
            return

        try:
            with open(filepath, 'w', newline='') as f:
                writer = csv.writer(f)

                # Escribir cabecera
                headers = ['Time_s', 'Power_W']
                if self.gpu_load:
                    headers.append('GPU_Load_%')
                if self.gpu_temp:
                    headers.append('GPU_Temp_C')

                writer.writerow(headers)

                # Escribir datos
                for i in range(len(self.power_readings)):
                    row = [f"{self.timestamps[i]:.3f}", f"{self.power_readings[i]:.2f}"]

                    if i < len(self.gpu_load):
                        row.append(f"{self.gpu_load[i]:.1f}")

                    if i < len(self.gpu_temp):
                        row.append(f"{self.gpu_temp[i]:.1f}")

                    writer.writerow(row)

            print(f"\n💾 Datos exportados a: {filepath}")

        except Exception as e:
            print(f"❌ Error al exportar: {e}")

    def plot_power(self, output_path=None):
        """Visualiza consumo de potencia."""
        try:
            import matplotlib.pyplot as plt

            fig, axes = plt.subplots(2, 1, figsize=(12, 8))
            fig.suptitle('Monitoreo de Potencia - IA Embarcada en Drones', fontsize=14)

            # Gráfico 1: Potencia a lo largo del tiempo
            ax1 = axes[0]
            ax1.plot(self.timestamps, self.power_readings, linewidth=2, color='#d62728', label='Potencia')
            ax1.axhline(y=np.mean(self.power_readings), color='orange', linestyle='--',
                       label=f'Media: {np.mean(self.power_readings):.2f}W')
            ax1.fill_between(self.timestamps, self.power_readings, alpha=0.3, color='#d62728')
            ax1.set_xlabel('Tiempo (s)')
            ax1.set_ylabel('Potencia (W)')
            ax1.set_title('Potencia en Tiempo Real')
            ax1.legend()
            ax1.grid(True, alpha=0.3)

            # Gráfico 2: Temperatura (si disponible)
            if self.gpu_temp:
                ax2 = axes[1]
                ax2.plot(self.timestamps, self.gpu_temp, linewidth=2, color='#ff7f0e', label='Temp GPU')
                ax2.axhline(y=80, color='red', linestyle='--', alpha=0.5, label='Límite crítico: 80°C')
                ax2.set_xlabel('Tiempo (s)')
                ax2.set_ylabel('Temperatura (°C)')
                ax2.set_title('Temperatura GPU')
                ax2.legend()
                ax2.grid(True, alpha=0.3)

            plt.tight_layout()

            if output_path:
                plt.savefig(output_path, dpi=150, bbox_inches='tight')
                print(f"💾 Gráfico guardado en: {output_path}")
            else:
                plt.show()

        except ImportError:
            print("⚠️  Matplotlib no disponible. Usa --plot <archivo> para ver gráficos")


def main():
    parser = argparse.ArgumentParser(
        description='Monitorear consumo energético durante inferencia YOLO',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python power_monitoring.py --model yolov8n.pt --frames 200
  python power_monitoring.py --model yolov8m.pt --duration 60
  python power_monitoring.py --model yolov8n.pt --export-csv power.csv
  python power_monitoring.py --model yolov8n.pt --plot power.png
        """
    )

    parser.add_argument('--model', type=str, default='yolov8n.pt',
                       help='Modelo YOLO a usar')
    parser.add_argument('--frames', type=int, default=100,
                       help='Número de frames a procesar')
    parser.add_argument('--duration', type=float, default=None,
                       help='Duración máxima en segundos')
    parser.add_argument('--interval', type=float, default=1.0,
                       help='Intervalo de muestreo en segundos')
    parser.add_argument('--export-csv', type=str, default=None,
                       help='Exportar datos a CSV')
    parser.add_argument('--plot', type=str, default=None,
                       help='Guardar gráficos')

    args = parser.parse_args()

    monitor = PowerMonitor(args.model, args.interval, args.duration)
    monitor.monitoring_loop(args.frames)

    if args.export_csv:
        monitor.export_csv(args.export_csv)

    if args.plot:
        monitor.plot_power(args.plot)


if __name__ == '__main__':
    main()
