#!/usr/bin/env python3
"""
Analizador de misiones de dron con YOLO v8.

Este script implementa un sistema que:
1. Procesa videos de vuelos de drones (grabaciones reales o simuladas)
2. Detecta objetos en cada frame usando YOLO v8
3. Genera reportes detallados por clase de objeto
4. Crea un timeline interactivo de detecciones
5. Exporta coordenadas geográficas (si hay metadata GPS) o estima posiciones

Concepto clave (del Capítulo 6):
    La telemetría del dron se combina con detecciones YOLO para generar
    un mapa espacio-temporal de objetos detectados durante la misión.

    Si la cámara tiene calibración conocida:
        geom_distance = (altura_objetivo * focal_length) / altura_bbox
        geo_location = (drone_lat, drone_lon) + bearing_offset

Uso:
    # Analizar video simple (sin GPS)
    python mission_analyzer.py --video mission.mp4 --model yolov8n.pt

    # Analizar video con datos telemetría (CSV con columnas: timestamp,lat,lon,alt)
    python mission_analyzer.py --video mission.mp4 --telemetry telemetry.csv

    # Análisis simulado con imágenes dummy
    python mission_analyzer.py --dummy --frames 300 --output mission_report.json

    # Exportar con visualización de timeline
    python mission_analyzer.py --video mission.mp4 --export-csv detections.csv \\
                               --export-json report.json --plot timeline.png

Requisitos:
    - pip install ultralytics opencv-python numpy pandas matplotlib
    - Modelo YOLO descargado (ej: yolov8n.pt)
    - Video en formato MP4, AVI, MOV (OpenCV)
    - Telemetría opcional: CSV con columnas (timestamp, lat, lon, alt)

Nota: Este es código educativo. Para análisis en producción:
    - Añadir sincronización GPS-video precisa
    - Validar detecciones con filtros de confianza
    - Implementar deduplicación (mismo objeto en múltiples frames)
    - Gestionar privacidad si hay personas detectadas
"""

import argparse
import time
import csv
import json
from collections import defaultdict
from pathlib import Path
from datetime import datetime, timedelta
import numpy as np

try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    print("⚠️  OpenCV no instalado")

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    print("⚠️  Ultralytics no instalada")

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    print("⚠️  Pandas no instalado (recomendado para exportación CSV)")

try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("⚠️  Matplotlib no instalado (necesario para gráficos)")


class MissionAnalyzer:
    """Analizador de misiones de dron con detecciones YOLO."""

    def __init__(self, model_path, telemetry_file=None, focal_length=615, person_height=1.7):
        """
        Inicializa el analizador de misiones.

        Args:
            model_path (str): Ruta del modelo YOLO
            telemetry_file (str): Ruta CSV con telemetría (timestamp, lat, lon, alt)
            focal_length (float): Parámetro de calibración (pixels)
            person_height (float): Altura estándar para personas (metros)
        """
        self.model_path = model_path
        self.focal_length = focal_length
        self.person_height = person_height

        # Cargar modelo
        if YOLO_AVAILABLE:
            self.model = YOLO(model_path)
        else:
            self.model = None

        # Cargar telemetría si existe
        self.telemetry = self._load_telemetry(telemetry_file)

        # Almacenamiento de resultados
        self.detections = []  # Lista de detecciones (frame, class, conf, bbox, lat, lon, alt)
        self.class_stats = defaultdict(lambda: {
            'count': 0,
            'confidence_sum': 0.0,
            'confidence_min': 1.0,
            'confidence_max': 0.0,
            'first_frame': None,
            'last_frame': None,
            'frames_present': []
        })

        # Estadísticas globales
        self.frame_count = 0
        self.total_detections = 0
        self.fps = 0.0

    def _load_telemetry(self, telemetry_file):
        """Carga datos de telemetría desde CSV."""
        if not telemetry_file or not Path(telemetry_file).exists():
            return None

        telemetry = {}
        try:
            with open(telemetry_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        frame_idx = int(row.get('frame', row.get('timestamp', 0)))
                        telemetry[frame_idx] = {
                            'lat': float(row['lat']),
                            'lon': float(row['lon']),
                            'alt': float(row.get('alt', 0.0))
                        }
                    except (ValueError, KeyError):
                        continue
            print(f"✅ Telemetría cargada: {len(telemetry)} frames con GPS")
            return telemetry
        except Exception as e:
            print(f"⚠️  Error cargando telemetría: {e}")
            return None

    def _get_drone_position(self, frame_idx):
        """Obtiene posición del dron para un frame dado."""
        if not self.telemetry:
            return None, None, None

        # Búsqueda exacta o interpolación
        if frame_idx in self.telemetry:
            t = self.telemetry[frame_idx]
            return t['lat'], t['lon'], t['alt']

        # Interpolación lineal entre frames adyacentes
        frames = sorted(self.telemetry.keys())
        for i in range(len(frames) - 1):
            if frames[i] < frame_idx < frames[i + 1]:
                t1 = self.telemetry[frames[i]]
                t2 = self.telemetry[frames[i + 1]]
                alpha = (frame_idx - frames[i]) / (frames[i + 1] - frames[i])

                lat = t1['lat'] + (t2['lat'] - t1['lat']) * alpha
                lon = t1['lon'] + (t2['lon'] - t1['lon']) * alpha
                alt = t1['alt'] + (t2['alt'] - t1['alt']) * alpha
                return lat, lon, alt

        return None, None, None

    def estimate_detection_location(self, frame_idx, bbox_center_x, bbox_center_y, frame_width, bbox_height):
        """
        Estima ubicación geográfica aproximada de una detección.

        Asume vista nadir (cámara apuntando hacia abajo) y cálculo simple.
        Para valores reales: usar calibración de cámara + rotación dron.
        """
        lat, lon, alt = self._get_drone_position(frame_idx)

        if lat is None:
            return None, None

        # Estimar distancia al objeto
        if bbox_height > 0:
            distance = (self.person_height * self.focal_length) / bbox_height
        else:
            distance = alt if alt else 10.0

        # Estimar offset lateral (muy simplificado)
        # En realidad se necesita: calibración K, rotación R, altura h
        frame_center_x = frame_width / 2
        lateral_ratio = (bbox_center_x - frame_center_x) / frame_center_x
        lateral_offset = lateral_ratio * distance * 0.1  # 0.1 = factor aprox

        # Aproximación: 1 grado ≈ 111 km
        lat_offset = lateral_offset / 111000.0  # Metros a grados
        lon_offset = lat_offset / np.cos(np.radians(lat))  # Ajustar por latitud

        estimated_lat = lat + lat_offset
        estimated_lon = lon + lon_offset

        return estimated_lat, estimated_lon

    def process_video(self, video_path):
        """Procesa video frame-by-frame y extrae detecciones."""
        if not OPENCV_AVAILABLE:
            print("❌ OpenCV necesario para procesar video")
            return False

        print(f"📹 Abriendo video: {video_path}")
        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            print("❌ No se pudo abrir el video")
            return False

        self.fps = cap.get(cv2.CAP_PROP_FPS)
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        print(f"🎬 Video: {frame_width}x{frame_height} @ {self.fps:.1f} FPS")
        print("🔍 Procesando frames...\n")

        self.frame_count = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            self._process_frame(frame, self.frame_count, frame_width, frame_height)
            self.frame_count += 1

            if self.frame_count % 30 == 0:
                print(f"   Frame {self.frame_count} — {self.total_detections} detecciones acumuladas")

        cap.release()
        print(f"\n✅ Procesamiento completo: {self.frame_count} frames, {self.total_detections} detecciones")
        return True

    def process_dummy_frames(self, num_frames):
        """Procesa frames dummy para prueba sin video."""
        print(f"📹 Usando {num_frames} frames dummy (640x480)")

        for frame_idx in range(num_frames):
            # Frame dummy con ruido
            frame = np.random.randint(50, 200, (480, 640, 3), dtype=np.uint8)

            # Inyectar algunas "detecciones" simuladas
            if frame_idx % 30 < 10:  # Simular objeto presente 10 frames de cada 30
                y = 100 + (frame_idx % 20) * 2
                x = 200 + int(50 * np.sin(frame_idx * 0.1))
                cv2.rectangle(frame, (x, y), (x + 80, y + 150), (0, 255, 0), 2)

            self._process_frame(frame, frame_idx, 640, 480)

            if (frame_idx + 1) % 50 == 0:
                print(f"   Frame {frame_idx + 1} — {self.total_detections} detecciones acumuladas")

        print(f"\n✅ Procesamiento completo: {num_frames} frames, {self.total_detections} detecciones")

    def _process_frame(self, frame, frame_idx, frame_width, frame_height):
        """Procesa un frame y extrae detecciones."""
        if self.model is None:
            return

        # Inferencia YOLO
        results = self.model(frame, conf=0.4, verbose=False)

        # Extraer detecciones
        for detection in results[0].boxes:
            x1, y1, x2, y2 = detection.xyxy[0].numpy()
            confidence = float(detection.conf[0])
            class_id = int(detection.cls[0])
            class_name = self.model.names[class_id]

            # Calcular centro y altura
            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2
            bbox_height = y2 - y1

            # Posición del dron
            lat, lon, alt = self._get_drone_position(frame_idx)

            # Estimar ubicación detección (si hay GPS)
            est_lat, est_lon = None, None
            if lat is not None:
                est_lat, est_lon = self.estimate_detection_location(
                    frame_idx, center_x, center_y, frame_width, bbox_height
                )

            # Guardar detección
            detection_record = {
                'frame': frame_idx,
                'class': class_name,
                'confidence': confidence,
                'bbox': (int(x1), int(y1), int(x2), int(y2)),
                'center': (int(center_x), int(center_y)),
                'drone_lat': lat,
                'drone_lon': lon,
                'drone_alt': alt,
                'estimated_lat': est_lat,
                'estimated_lon': est_lon
            }

            self.detections.append(detection_record)
            self.total_detections += 1

            # Actualizar estadísticas por clase
            stats = self.class_stats[class_name]
            stats['count'] += 1
            stats['confidence_sum'] += confidence
            stats['confidence_min'] = min(stats['confidence_min'], confidence)
            stats['confidence_max'] = max(stats['confidence_max'], confidence)
            if stats['first_frame'] is None:
                stats['first_frame'] = frame_idx
            stats['last_frame'] = frame_idx
            stats['frames_present'].append(frame_idx)

    def print_statistics(self):
        """Imprime estadísticas del análisis."""
        print("\n" + "=" * 80)
        print("📊 ESTADÍSTICAS DE MISIÓN")
        print("=" * 80)
        print(f"Total de frames procesados:     {self.frame_count}")
        print(f"Framerate (FPS):                {self.fps:.1f}")
        print(f"Duración estimada (min):        {self.frame_count / (self.fps * 60):.2f}")
        print(f"Total de detecciones:           {self.total_detections}")

        if self.frame_count > 0:
            detection_rate = (self.total_detections / self.frame_count) * 100
            print(f"Densidad (detecciones/frame):   {detection_rate:.2f}")

        print("\n📋 DETECCIONES POR CLASE:")
        print("-" * 80)

        for class_name in sorted(self.class_stats.keys()):
            stats = self.class_stats[class_name]
            avg_conf = stats['confidence_sum'] / stats['count']
            duration_frames = stats['last_frame'] - stats['first_frame'] + 1

            print(f"\n  {class_name.upper()}:")
            print(f"    Conteo total:               {stats['count']}")
            print(f"    Confianza promedio:         {avg_conf:.3f}")
            print(f"    Confianza rango:            [{stats['confidence_min']:.3f}, {stats['confidence_max']:.3f}]")
            print(f"    Primer frame:               {stats['first_frame']}")
            print(f"    Último frame:               {stats['last_frame']}")
            print(f"    Duración (frames):          {duration_frames}")
            print(f"    Tasa de aparición:          {(stats['count'] / duration_frames * 100):.1f}% de frames")

        print("\n" + "=" * 80)

    def export_csv(self, output_path):
        """Exporta detecciones a CSV."""
        if not self.detections:
            print("⚠️  No hay detecciones para exportar")
            return

        print(f"\n💾 Exportando detecciones a: {output_path}")

        try:
            with open(output_path, 'w', newline='') as f:
                fieldnames = [
                    'frame', 'class', 'confidence',
                    'bbox_x1', 'bbox_y1', 'bbox_x2', 'bbox_y2',
                    'center_x', 'center_y',
                    'drone_lat', 'drone_lon', 'drone_alt',
                    'estimated_lat', 'estimated_lon'
                ]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()

                for det in self.detections:
                    x1, y1, x2, y2 = det['bbox']
                    cx, cy = det['center']
                    writer.writerow({
                        'frame': det['frame'],
                        'class': det['class'],
                        'confidence': f"{det['confidence']:.4f}",
                        'bbox_x1': x1, 'bbox_y1': y1, 'bbox_x2': x2, 'bbox_y2': y2,
                        'center_x': cx, 'center_y': cy,
                        'drone_lat': det['drone_lat'],
                        'drone_lon': det['drone_lon'],
                        'drone_alt': det['drone_alt'],
                        'estimated_lat': det['estimated_lat'],
                        'estimated_lon': det['estimated_lon']
                    })

            print(f"✅ Exportado: {len(self.detections)} detecciones")
        except Exception as e:
            print(f"❌ Error exportando CSV: {e}")

    def export_json(self, output_path):
        """Exporta reporte completo a JSON."""
        print(f"\n💾 Exportando reporte JSON a: {output_path}")

        report = {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'total_frames': self.frame_count,
                'total_detections': self.total_detections,
                'fps': self.fps,
                'duration_seconds': self.frame_count / self.fps if self.fps > 0 else 0
            },
            'class_summary': {},
            'detections': self.detections
        }

        # Agregar resumen por clase
        for class_name, stats in self.class_stats.items():
            report['class_summary'][class_name] = {
                'count': stats['count'],
                'avg_confidence': stats['confidence_sum'] / stats['count'],
                'min_confidence': float(stats['confidence_min']),
                'max_confidence': float(stats['confidence_max']),
                'first_frame': stats['first_frame'],
                'last_frame': stats['last_frame']
            }

        try:
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            print(f"✅ Exportado reporte JSON")
        except Exception as e:
            print(f"❌ Error exportando JSON: {e}")

    def plot_timeline(self, output_path):
        """Genera gráfico de timeline de detecciones."""
        if not MATPLOTLIB_AVAILABLE:
            print("⚠️  Matplotlib necesario para gráficos")
            return

        print(f"\n📊 Generando timeline: {output_path}")

        try:
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8))

            # Gráfico 1: Detecciones por frame
            detections_per_frame = defaultdict(int)
            for det in self.detections:
                detections_per_frame[det['frame']] += 1

            frames = sorted(detections_per_frame.keys())
            counts = [detections_per_frame[f] for f in frames]

            ax1.bar(frames, counts, width=1.0, alpha=0.7, color='steelblue')
            ax1.set_xlabel('Frame')
            ax1.set_ylabel('Detecciones por frame')
            ax1.set_title('Timeline: Densidad de Detecciones')
            ax1.grid(True, alpha=0.3)

            # Gráfico 2: Confianza promedio por clase
            class_names = sorted(self.class_stats.keys())
            avg_confs = []

            for class_name in class_names:
                stats = self.class_stats[class_name]
                avg_conf = stats['confidence_sum'] / stats['count']
                avg_confs.append(avg_conf)

            colors = plt.cm.Set3(np.linspace(0, 1, len(class_names)))
            ax2.bar(range(len(class_names)), avg_confs, color=colors)
            ax2.set_xticks(range(len(class_names)))
            ax2.set_xticklabels(class_names, rotation=45, ha='right')
            ax2.set_ylabel('Confianza promedio')
            ax2.set_title('Confianza de Detección por Clase')
            ax2.set_ylim([0, 1.0])
            ax2.grid(True, alpha=0.3, axis='y')

            plt.tight_layout()
            plt.savefig(output_path, dpi=100, bbox_inches='tight')
            print(f"✅ Gráfico guardado: {output_path}")
            plt.close()

        except Exception as e:
            print(f"❌ Error generando gráfico: {e}")


def main():
    parser = argparse.ArgumentParser(
        description='Analizador de misiones de dron con YOLO v8',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python mission_analyzer.py --video mission.mp4 --model yolov8n.pt
  python mission_analyzer.py --video mission.mp4 --telemetry telem.csv --export-csv detections.csv
  python mission_analyzer.py --dummy --frames 300 --export-json report.json
  python mission_analyzer.py --video flight.mp4 --plot timeline.png --export-json analysis.json
        """
    )

    parser.add_argument('--video', type=str, help='Ruta del archivo de video')
    parser.add_argument('--dummy', action='store_true', help='Usar frames dummy (sin video real)')
    parser.add_argument('--frames', type=int, default=300, help='Número de frames para modo dummy')
    parser.add_argument('--model', type=str, default='yolov8n.pt', help='Modelo YOLO a usar')
    parser.add_argument('--telemetry', type=str, help='Archivo CSV con telemetría (frame, lat, lon, alt)')
    parser.add_argument('--focal-length', type=float, default=615, help='Focal length de cámara (pixels)')
    parser.add_argument('--export-csv', type=str, help='Exportar detecciones a CSV')
    parser.add_argument('--export-json', type=str, help='Exportar reporte a JSON')
    parser.add_argument('--plot', type=str, help='Generar gráfico timeline (PNG)')

    args = parser.parse_args()

    if not args.video and not args.dummy:
        parser.print_help()
        return

    analyzer = MissionAnalyzer(
        model_path=args.model,
        telemetry_file=args.telemetry,
        focal_length=args.focal_length
    )

    print("🚁 ANALIZADOR DE MISIONES DE DRON")
    print("=" * 80)

    # Procesar fuente
    if args.dummy:
        analyzer.process_dummy_frames(args.frames)
    else:
        if not analyzer.process_video(args.video):
            return

    # Mostrar estadísticas
    analyzer.print_statistics()

    # Exportar resultados
    if args.export_csv:
        analyzer.export_csv(args.export_csv)

    if args.export_json:
        analyzer.export_json(args.export_json)

    if args.plot:
        analyzer.plot_timeline(args.plot)


if __name__ == '__main__':
    main()
