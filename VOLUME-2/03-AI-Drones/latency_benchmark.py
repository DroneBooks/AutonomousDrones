#!/usr/bin/env python3
"""
Medición detallada de latencia de inferencia en modelos YOLO.

Este script analiza la latencia total en un pipeline de IA embarcada,
desglosando dónde se consume el tiempo (captura, preprocesamiento,
inferencia, postprocesamiento).

Concepto clave (del Capítulo 3 del libro):
    Latencia total = captura + preproceso + inferencia + postproceso + envío

En drones, mantener esta latencia < 100ms es crítico para control en tiempo real.

Uso:
    python latency_benchmark.py --model yolov8n.pt
    python latency_benchmark.py --model yolov8m.pt --source webcam
    python latency_benchmark.py --model yolov8s.engine --source video.mp4
    python latency_benchmark.py --model yolov8n.pt --export-csv latencies.csv

Requisitos:
    - ultralytics (YOLO v8)
    - opencv-python
    - numpy
    - matplotlib (opcional, para gráficos)
"""

import argparse
import time
import csv
from pathlib import Path
from collections import deque
import numpy as np

try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    print("⚠️  OpenCV no instalado. Instala con: pip install opencv-python")

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    print("⚠️  Ultralytics no instalada. Instala con: pip install ultralytics")

try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


class LatencyBenchmark:
    """Mide latencia detallada de pipeline de inferencia."""

    def __init__(self, model_path, source='webcam', max_samples=500):
        """
        Inicializa el benchmark.

        Args:
            model_path (str): Ruta del modelo YOLO
            source (str): Fuente de video ('webcam', ruta archivo, o 'dummy')
            max_samples (int): Máximo número de muestras a recopilar
        """
        self.model_path = model_path
        self.source = source
        self.max_samples = max_samples

        # Historial de latencias (últimas 100 muestras para estadística en vivo)
        self.latency_window = deque(maxlen=100)

        # Estadísticas desglosadas
        self.capture_times = []
        self.preprocess_times = []
        self.inference_times = []
        self.postprocess_times = []
        self.total_times = []

        # Cargar modelo
        if YOLO_AVAILABLE:
            self.model = YOLO(model_path)
        else:
            self.model = None

    def open_video_source(self):
        """Abre la fuente de video (webcam, archivo, o dummy)."""
        if not OPENCV_AVAILABLE:
            print("❌ OpenCV necesario para capturar video")
            return None

        if self.source == 'webcam':
            print("📷 Abriendo webcam...")
            cap = cv2.VideoCapture(0)

            if not cap.isOpened():
                print("❌ No se pudo abrir la webcam")
                return None

            # Configurar resolución
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            cap.set(cv2.CAP_PROP_FPS, 30)

        elif self.source == 'dummy':
            print("🎬 Usando imágenes dummy (640x480)")
            return None  # Lo manejaremos especialmente

        else:
            print(f"📹 Abriendo archivo: {self.source}")
            cap = cv2.VideoCapture(self.source)

            if not cap.isOpened():
                print(f"❌ No se pudo abrir: {self.source}")
                return None

        return cap

    def benchmark_loop(self, num_frames=100):
        """
        Ejecuta el loop de benchmark.

        Args:
            num_frames (int): Número de frames a procesar
        """
        if self.model is None:
            print("❌ Modelo no cargado")
            return

        cap = self.open_video_source()

        print(f"\n⏱️  Iniciando benchmark ({num_frames} frames)...")
        print("   Frame | Captura | Prepro | Infer | Postpro | Total")
        print("   " + "-" * 50)

        frames_processed = 0

        for frame_idx in range(num_frames):
            # Captura
            t_capture_start = time.perf_counter()

            if self.source == 'dummy':
                # Imagen dummy si no hay webcam/video
                frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
            else:
                ret, frame = cap.read()
                if not ret:
                    print("   Fin del video")
                    break

            t_capture_end = time.perf_counter()
            capture_time = (t_capture_end - t_capture_start) * 1000

            # Preprocesamiento (YOLO lo hace internamente, pero lo estimamos)
            t_preprocess_start = time.perf_counter()
            # En YOLO, el preprocesamiento incluye redimensionamiento y normalización
            frame_resized = cv2.resize(frame, (640, 640))
            t_preprocess_end = time.perf_counter()
            preprocess_time = (t_preprocess_end - t_preprocess_start) * 1000

            # Inferencia
            t_inference_start = time.perf_counter()
            results = self.model(frame_resized, verbose=False)
            t_inference_end = time.perf_counter()
            inference_time = (t_inference_end - t_inference_start) * 1000

            # Postprocesamiento (extraer detecciones)
            t_postprocess_start = time.perf_counter()
            detections = results[0].boxes.data if results else []
            t_postprocess_end = time.perf_counter()
            postprocess_time = (t_postprocess_end - t_postprocess_start) * 1000

            # Latencia total
            total_time = capture_time + preprocess_time + inference_time + postprocess_time

            # Registrar
            self.capture_times.append(capture_time)
            self.preprocess_times.append(preprocess_time)
            self.inference_times.append(inference_time)
            self.postprocess_times.append(postprocess_time)
            self.total_times.append(total_time)
            self.latency_window.append(total_time)

            # Mostrar progreso
            print(f"   {frame_idx + 1:3d}   | {capture_time:6.2f}  | {preprocess_time:5.2f}  | "
                  f"{inference_time:5.2f} | {postprocess_time:6.2f}  | {total_time:6.2f}")

            frames_processed += 1

            if frames_processed >= self.max_samples:
                break

        if cap:
            cap.release()

        self.print_statistics()

    def print_statistics(self):
        """Imprime estadísticas detalladas de latencia."""
        if not self.total_times:
            print("❌ No hay datos para analizar")
            return

        total = np.array(self.total_times)
        capture = np.array(self.capture_times)
        preprocess = np.array(self.preprocess_times)
        inference = np.array(self.inference_times)
        postprocess = np.array(self.postprocess_times)

        print("\n" + "="*70)
        print("📊 ESTADÍSTICAS DE LATENCIA (ms)")
        print("="*70)

        print(f"\n🔹 LATENCIA TOTAL:")
        print(f"   Media:        {np.mean(total):.2f} ms")
        print(f"   Mediana:      {np.median(total):.2f} ms")
        print(f"   Percentil 95: {np.percentile(total, 95):.2f} ms")
        print(f"   Percentil 99: {np.percentile(total, 99):.2f} ms")
        print(f"   Min:          {np.min(total):.2f} ms")
        print(f"   Max:          {np.max(total):.2f} ms")
        print(f"   Desv. Est:    {np.std(total):.2f} ms")

        print(f"\n🔹 DESGLOSE POR COMPONENTE (media):")
        total_mean = np.mean(total)
        print(f"   Captura:        {np.mean(capture):6.2f} ms ({np.mean(capture)/total_mean*100:5.1f}%)")
        print(f"   Preprocesado:   {np.mean(preprocess):6.2f} ms ({np.mean(preprocess)/total_mean*100:5.1f}%)")
        print(f"   Inferencia:     {np.mean(inference):6.2f} ms ({np.mean(inference)/total_mean*100:5.1f}%)")
        print(f"   Postprocesado:  {np.mean(postprocess):6.2f} ms ({np.mean(postprocess)/total_mean*100:5.1f}%)")

        # Verificar si está apto para drones
        print(f"\n⚡ EVALUACIÓN PARA DRONES:")
        if np.mean(total) < 50:
            print(f"   ✅ EXCELENTE: Latencia < 50ms (>20 FPS) — Apto para control en tiempo real")
        elif np.mean(total) < 100:
            print(f"   ✅ BUENO: Latencia < 100ms (>10 FPS) — Apto para la mayoría de aplicaciones")
        elif np.mean(total) < 200:
            print(f"   ⚠️  ACEPTABLE: Latencia < 200ms (>5 FPS) — Solo para decisiones no críticas")
        else:
            print(f"   ❌ ALTO RIESGO: Latencia > 200ms (<5 FPS) — NO apto para drones en vuelo")

        print("="*70)

    def export_csv(self, filepath):
        """Exporta datos detallados a CSV."""
        if not self.total_times:
            print("❌ No hay datos para exportar")
            return

        try:
            with open(filepath, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Frame', 'Capture_ms', 'Preprocess_ms', 'Inference_ms', 'Postprocess_ms', 'Total_ms'])

                for i in range(len(self.total_times)):
                    writer.writerow([
                        i,
                        f"{self.capture_times[i]:.4f}",
                        f"{self.preprocess_times[i]:.4f}",
                        f"{self.inference_times[i]:.4f}",
                        f"{self.postprocess_times[i]:.4f}",
                        f"{self.total_times[i]:.4f}",
                    ])

            print(f"\n💾 Datos exportados a: {filepath}")

        except Exception as e:
            print(f"❌ Error al exportar: {e}")

    def plot_latency(self, output_path=None):
        """Visualiza latencia en gráfico."""
        if not MATPLOTLIB_AVAILABLE or not self.total_times:
            return

        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        fig.suptitle('Análisis de Latencia - Pipeline IA Embarcada', fontsize=14, fontweight='bold')

        # Gráfico 1: Latencia total a lo largo del tiempo
        ax1 = axes[0, 0]
        ax1.plot(self.total_times, linewidth=1.5, color='#1f77b4')
        ax1.axhline(y=np.mean(self.total_times), color='r', linestyle='--', label=f'Media: {np.mean(self.total_times):.2f}ms')
        ax1.axhline(y=100, color='orange', linestyle='--', alpha=0.5, label='Umbral drones: 100ms')
        ax1.set_xlabel('Frame')
        ax1.set_ylabel('Latencia (ms)')
        ax1.set_title('Latencia Total')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Gráfico 2: Desglose por componente (stacked area)
        ax2 = axes[0, 1]
        ax2.fill_between(range(len(self.total_times)), 0, self.capture_times, alpha=0.5, label='Captura')
        ax2.fill_between(range(len(self.total_times)), self.capture_times,
                         np.array(self.capture_times) + np.array(self.preprocess_times),
                         alpha=0.5, label='Preproceso')
        ax2.fill_between(range(len(self.total_times)),
                         np.array(self.capture_times) + np.array(self.preprocess_times),
                         np.array(self.total_times) - np.array(self.postprocess_times),
                         alpha=0.5, label='Inferencia')
        ax2.fill_between(range(len(self.total_times)),
                         np.array(self.total_times) - np.array(self.postprocess_times),
                         np.array(self.total_times),
                         alpha=0.5, label='Postproceso')
        ax2.set_xlabel('Frame')
        ax2.set_ylabel('Latencia (ms)')
        ax2.set_title('Desglose de Componentes')
        ax2.legend(loc='upper left', fontsize=8)
        ax2.grid(True, alpha=0.3)

        # Gráfico 3: Distribución de latencia (histogram)
        ax3 = axes[1, 0]
        ax3.hist(self.total_times, bins=30, alpha=0.7, color='#2ca02c', edgecolor='black')
        ax3.axvline(x=np.mean(self.total_times), color='r', linestyle='--', linewidth=2, label='Media')
        ax3.axvline(x=np.percentile(self.total_times, 95), color='orange', linestyle='--', linewidth=2, label='P95')
        ax3.set_xlabel('Latencia (ms)')
        ax3.set_ylabel('Frecuencia')
        ax3.set_title('Distribución de Latencias')
        ax3.legend()
        ax3.grid(True, alpha=0.3, axis='y')

        # Gráfico 4: Componentes (box plot)
        ax4 = axes[1, 1]
        data = [self.capture_times, self.preprocess_times, self.inference_times, self.postprocess_times]
        labels = ['Captura', 'Preproceso', 'Inferencia', 'Postproceso']
        bp = ax4.boxplot(data, labels=labels, patch_artist=True)

        for patch, color in zip(bp['boxes'], ['#ff7f0e', '#2ca02c', '#d62728', '#9467bd']):
            patch.set_facecolor(color)

        ax4.set_ylabel('Latencia (ms)')
        ax4.set_title('Distribución por Componente')
        ax4.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()

        if output_path:
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            print(f"💾 Gráfico guardado en: {output_path}")
        else:
            plt.show()


def main():
    parser = argparse.ArgumentParser(
        description='Medir latencia detallada de pipeline YOLO en drones',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python latency_benchmark.py --model yolov8n.pt --source webcam --frames 200
  python latency_benchmark.py --model yolov8n.engine --source video.mp4
  python latency_benchmark.py --model yolov8m.pt --export-csv results.csv
  python latency_benchmark.py --model yolov8n.pt --plot latency.png
        """
    )

    parser.add_argument('--model', type=str, default='yolov8n.pt',
                       help='Modelo YOLO (.pt o .engine)')
    parser.add_argument('--source', type=str, default='dummy',
                       help='Fuente de video: webcam, ruta archivo, o dummy')
    parser.add_argument('--frames', type=int, default=100,
                       help='Número de frames a procesar')
    parser.add_argument('--export-csv', type=str, default=None,
                       help='Exportar datos a CSV')
    parser.add_argument('--plot', type=str, default=None,
                       help='Guardar gráficos en archivo')

    args = parser.parse_args()

    benchmark = LatencyBenchmark(args.model, args.source)
    benchmark.benchmark_loop(args.frames)

    if args.export_csv:
        benchmark.export_csv(args.export_csv)

    if args.plot:
        benchmark.plot_latency(args.plot)
    elif MATPLOTLIB_AVAILABLE:
        print("\n💡 Tip: Usa --plot <archivo> para guardar gráficos")


if __name__ == '__main__':
    main()
