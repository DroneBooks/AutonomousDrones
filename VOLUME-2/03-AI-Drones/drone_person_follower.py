#!/usr/bin/env python3
"""
Dron seguidor de personas usando YOLO v8 y estimación de distancia.

Este script implementa un sistema que:
1. Detecta personas en video (YOLO v8)
2. Estima distancia usando altura conocida de persona (1.7m)
3. Mantiene distancia constante (ej: 2 metros)
4. Envía comandos de control (velocidad forward/back, turn)

Concepto clave (del Capítulo 6):
    El dron calcula la distancia a la persona basándose en el tamaño
    del bounding box (asume altura estándar de 1.7m en el frame).

    distancia = (altura_real * focal_length) / altura_bbox

Uso:
    # Seguidor en tiempo real con webcam
    python drone_person_follower.py --model yolov8n.pt --source webcam

    # Seguidor con video
    python drone_person_follower.py --model yolov8n.pt --source video.mp4

    # Simulación con imágenes dummy
    python drone_person_follower.py --model yolov8n.pt --source dummy --frames 100

Requisitos (además de los básicos):
    - pip install pymavlink (para comunicación con Pixhawk)
    - Cámara calibrada (conocer focal_length)
    - Pixhawk con Ardupilot (para control real) o simulador SITL

Nota: Este es un código educativo. Para uso en dron real:
    - Añadir failsafe si pierde seguimiento
    - Validar distancia antes de ejecutar
    - Implementar anti-oscilaciones (PID control)
"""

import argparse
import time
import numpy as np
from collections import deque

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
    from pymavlink.mavutil import mavlink_connection
    PYMAVLINK_AVAILABLE = True
except ImportError:
    PYMAVLINK_AVAILABLE = False
    print("⚠️  pymavlink no instalado (necesario para Pixhawk real)")


class PersonFollower:
    """Dron que sigue a personas manteniendo distancia constante."""

    def __init__(self, model_path, target_distance=2.0, focal_length=615):
        """
        Inicializa el seguidor de personas.

        Args:
            model_path (str): Ruta del modelo YOLO
            target_distance (float): Distancia objetivo a mantener (metros)
            focal_length (float): Parámetro de calibración de cámara (pixels)
                                 Típicamente 600-650 para cámaras estándar
        """
        self.model_path = model_path
        self.target_distance = target_distance
        self.focal_length = focal_length

        # Cargar modelo
        if YOLO_AVAILABLE:
            self.model = YOLO(model_path)
        else:
            self.model = None

        # Parámetros de persona
        self.person_height_real = 1.7  # Altura promedio persona en metros

        # Control PID (simple)
        self.distance_error_history = deque(maxlen=10)
        self.kp_distance = 0.3  # Proporcional para control de distancia
        self.kp_lateral = 0.5  # Proporcional para control lateral

        # Estadísticas
        self.frame_count = 0
        self.person_detected_frames = 0
        self.lost_tracking_count = 0

    def estimate_distance(self, bbox_height):
        """
        Estima distancia a persona basándose en altura del bounding box.

        Fórmula: distance = (person_height_real * focal_length) / bbox_height

        Args:
            bbox_height (float): Altura del bounding box en pixels

        Returns:
            float: Distancia estimada en metros
        """
        if bbox_height <= 0:
            return float('inf')

        distance = (self.person_height_real * self.focal_length) / bbox_height
        return distance

    def calculate_control_command(self, frame, detections):
        """
        Calcula comando de control basado en detección.

        Returns:
            dict: {
                'forward_back': [-1.0, 1.0],  # -1=back, 0=stop, 1=forward
                'left_right': [-1.0, 1.0],    # -1=left, 0=center, 1=right
                'distance': float,
                'confidence': float,
            }
        """
        frame_height, frame_width = frame.shape[:2]
        frame_center_x = frame_width / 2

        # Buscar persona más grande (más cercana)
        largest_person = None
        largest_area = 0

        for detection in detections:
            x1, y1, x2, y2 = detection['bbox']
            class_name = detection['class']

            if class_name != 'person':
                continue

            bbox_area = (x2 - x1) * (y2 - y1)
            if bbox_area > largest_area:
                largest_area = bbox_area
                largest_person = detection

        # Si no hay persona, devolver comando de parada
        if largest_person is None:
            self.lost_tracking_count += 1
            return {
                'forward_back': 0.0,
                'left_right': 0.0,
                'distance': None,
                'confidence': 0.0,
                'status': 'LOST'
            }

        # Persona detectada
        self.person_detected_frames += 1
        self.lost_tracking_count = 0

        # Extraer datos
        x1, y1, x2, y2 = largest_person['bbox']
        confidence = largest_person['confidence']
        center_x = (x1 + x2) / 2
        bbox_height = y2 - y1

        # Estimar distancia
        distance = self.estimate_distance(bbox_height)

        # CONTROL DE DISTANCIA
        distance_error = distance - self.target_distance
        self.distance_error_history.append(distance_error)

        # Control proporcional simple
        forward_back = -self.kp_distance * distance_error
        forward_back = np.clip(forward_back, -1.0, 1.0)

        # CONTROL LATERAL (mantener centrado)
        lateral_error = center_x - frame_center_x
        left_right = -self.kp_lateral * (lateral_error / frame_width)
        left_right = np.clip(left_right, -1.0, 1.0)

        # Determinar estado
        if abs(distance_error) < 0.3:
            status = "CENTERED"
        elif distance_error > 0:
            status = "TOO_FAR"
        else:
            status = "TOO_CLOSE"

        return {
            'forward_back': forward_back,
            'left_right': left_right,
            'distance': distance,
            'confidence': confidence,
            'status': status
        }

    def process_frame(self, frame):
        """
        Procesa un frame y calcula comando de control.

        Args:
            frame (ndarray): Imagen de entrada (OpenCV format)

        Returns:
            dict: Comando de control + visualización (frame anotado)
        """
        if self.model is None:
            return None, frame

        self.frame_count += 1

        # Inferencia YOLO
        results = self.model(frame, conf=0.5, verbose=False)

        # Extraer detecciones
        detections = []
        for detection in results[0].boxes:
            x1, y1, x2, y2 = detection.xyxy[0].numpy()
            confidence = float(detection.conf[0])
            class_id = int(detection.cls[0])
            class_name = self.model.names[class_id]

            detections.append({
                'bbox': (x1, y1, x2, y2),
                'class': class_name,
                'confidence': confidence
            })

        # Calcular comando
        command = self.calculate_control_command(frame, detections)

        # Visualizar
        annotated_frame = self._draw_annotations(frame, detections, command)

        return command, annotated_frame

    def _draw_annotations(self, frame, detections, command):
        """Dibuja detecciones y estado en el frame."""
        annotated = frame.copy()
        frame_height, frame_width = frame.shape[:2]

        # Dibujar línea central
        cv2.line(annotated, (frame_width // 2, 0), (frame_width // 2, frame_height),
                (0, 255, 0), 2)

        # Dibujar zona de distancia objetivo (rectángulo indicativo)
        # Asumiendo distancia = altura_real * focal / bbox_height
        # Si bbox_height = (altura_real * focal) / target_distance
        target_bbox_height = int((self.person_height_real * self.focal_length) / self.target_distance)
        if target_bbox_height < frame_height:
            rect_height = target_bbox_height
            rect_width = int(rect_height * 0.5)  # Asume aspecto 2:1
            x1 = (frame_width - rect_width) // 2
            y1 = (frame_height - rect_height) // 2
            cv2.rectangle(annotated, (x1, y1), (x1 + rect_width, y1 + rect_height),
                         (255, 255, 0), 2)  # Azul cian - zona objetivo

        # Dibujar detecciones
        for detection in detections:
            x1, y1, x2, y2 = detection['bbox']
            class_name = detection['class']
            confidence = detection['confidence']

            if class_name == 'person':
                cv2.rectangle(annotated, (int(x1), int(y1)), (int(x2), int(y2)),
                            (0, 255, 0), 2)  # Verde para personas
                cv2.putText(annotated, f'{class_name} {confidence:.2f}',
                          (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX,
                          0.5, (0, 255, 0), 2)

        # Mostrar comando y estado
        if command['status'] != 'LOST':
            text = f"Status: {command['status']}"
            color = (0, 255, 0) if command['status'] == 'CENTERED' else (0, 165, 255)
            cv2.putText(annotated, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                       1, color, 2)

            if command['distance'] is not None:
                dist_text = f"Distance: {command['distance']:.1f}m (target: {self.target_distance}m)"
                cv2.putText(annotated, dist_text, (10, 70), cv2.FONT_HERSHEY_SIMPLEX,
                          0.7, (255, 255, 255), 2)

            # Mostrar comandos de control
            cmd_text = f"Forward: {command['forward_back']:+.2f} | Lateral: {command['left_right']:+.2f}"
            cv2.putText(annotated, cmd_text, (10, 110), cv2.FONT_HERSHEY_SIMPLEX,
                       0.7, (255, 255, 255), 2)
        else:
            cv2.putText(annotated, "TRACKING LOST", (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                       1, (0, 0, 255), 2)

        # Mostrar FPS
        fps_text = f"FPS: {self.frame_count} | Detected: {self.person_detected_frames}"
        cv2.putText(annotated, fps_text, (10, frame_height - 20), cv2.FONT_HERSHEY_SIMPLEX,
                   0.6, (200, 200, 200), 1)

        return annotated

    def run_follower(self, source='webcam', max_frames=None, display=True):
        """
        Ejecuta el seguidor de personas.

        Args:
            source (str): 'webcam', 'dummy', o ruta de video
            max_frames (int): Máximo número de frames a procesar
            display (bool): Mostrar video en pantalla
        """
        if source == 'dummy':
            print("📹 Usando frames dummy (640x480)")
            cap = None
        else:
            if not OPENCV_AVAILABLE:
                print("❌ OpenCV necesario")
                return

            if source == 'webcam':
                print("📷 Abriendo webcam...")
                cap = cv2.VideoCapture(0)
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            else:
                print(f"📹 Abriendo video: {source}")
                cap = cv2.VideoCapture(source)

            if cap and not cap.isOpened():
                print("❌ No se pudo abrir la fuente de video")
                return

        print(f"🎯 Iniciando seguidor de personas (distancia objetivo: {self.target_distance}m)")
        print("   Presiona 'q' para salir\n")

        frame_idx = 0

        while True:
            # Obtener frame
            if source == 'dummy':
                frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
            else:
                ret, frame = cap.read()
                if not ret:
                    print("Fin del video")
                    break

            # Procesar
            command, annotated_frame = self.process_frame(frame)

            # Mostrar
            if display and OPENCV_AVAILABLE:
                cv2.imshow('Person Follower', annotated_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            frame_idx += 1
            if max_frames and frame_idx >= max_frames:
                break

        # Mostrar estadísticas
        self._print_statistics()

        if cap:
            cap.release()
        if OPENCV_AVAILABLE:
            cv2.destroyAllWindows()

    def _print_statistics(self):
        """Imprime estadísticas del seguidor."""
        print("\n" + "="*70)
        print("📊 ESTADÍSTICAS DEL SEGUIDOR")
        print("="*70)
        print(f"Frames procesados:           {self.frame_count}")
        print(f"Frames con persona:          {self.person_detected_frames}")
        print(f"Frames sin persona (lost):   {self.lost_tracking_count}")

        if self.frame_count > 0:
            detection_rate = (self.person_detected_frames / self.frame_count) * 100
            print(f"Tasa de detección:           {detection_rate:.1f}%")

        print("="*70)


def main():
    parser = argparse.ArgumentParser(
        description='Dron seguidor de personas usando YOLO v8',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python drone_person_follower.py --model yolov8n.pt --source webcam
  python drone_person_follower.py --model yolov8n.pt --source video.mp4
  python drone_person_follower.py --model yolov8n.pt --source dummy --frames 200
  python drone_person_follower.py --model yolov8n.engine --distance 3.0
        """
    )

    parser.add_argument('--model', type=str, default='yolov8n.pt',
                       help='Modelo YOLO a usar')
    parser.add_argument('--source', type=str, default='dummy',
                       help='Fuente: webcam, ruta de video, o dummy')
    parser.add_argument('--distance', type=float, default=2.0,
                       help='Distancia objetivo a mantener (metros)')
    parser.add_argument('--focal-length', type=float, default=615,
                       help='Focal length de cámara (calibración)')
    parser.add_argument('--frames', type=int, default=None,
                       help='Máximo frames a procesar (None = indefinido)')
    parser.add_argument('--no-display', action='store_true',
                       help='No mostrar video (headless mode)')

    args = parser.parse_args()

    follower = PersonFollower(
        model_path=args.model,
        target_distance=args.distance,
        focal_length=args.focal_length
    )

    follower.run_follower(
        source=args.source,
        max_frames=args.frames,
        display=not args.no_display
    )


if __name__ == '__main__':
    main()
