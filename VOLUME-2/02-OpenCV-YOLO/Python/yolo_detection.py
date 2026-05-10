#!/usr/bin/env python3
"""
Volumen 2 — Capítulo 2: OpenCV+YOLO — Detección YOLO v8 en Tiempo Real
Realiza detección de objetos usando YOLOv8 en webcam o archivo de video
"""

import cv2
import sys
from ultralytics import YOLO

class YOLODetector:
    """Detector de objetos con YOLO v8"""

    def __init__(self, model_size='n'):
        """
        Inicializa el modelo YOLO

        Args:
            model_size: Tamaño del modelo ('n', 's', 'm', 'l', 'x')
                       'n' = nano (rápido, bajo recursos)
                       'x' = extra large (lento, más preciso)
        """
        model_names = {
            'n': 'yolov8n.pt',
            's': 'yolov8s.pt',
            'm': 'yolov8m.pt',
            'l': 'yolov8l.pt',
            'x': 'yolov8x.pt'
        }

        model_name = model_names.get(model_size, 'yolov8n.pt')
        print(f"[*] Cargando modelo {model_name}...")

        self.model = YOLO(model_name)
        print("[OK] Modelo cargado")

    def detect_frame(self, frame, conf_threshold=0.5):
        """
        Realiza detección en un frame

        Args:
            frame: Imagen (numpy array)
            conf_threshold: Umbral de confianza (0-1)

        Returns:
            Imagen con detecciones dibujadas, lista de detecciones
        """
        results = self.model(frame, conf=conf_threshold, verbose=False)
        result = results[0]

        detections = []

        if result.boxes is not None:
            for box in result.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                class_id = int(box.cls[0])
                class_name = self.model.names[class_id]

                detections.append({
                    'bbox': (x1, y1, x2, y2),
                    'confidence': conf,
                    'class_id': class_id,
                    'class_name': class_name
                })

                # Dibujar bounding box
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

                # Dibujar etiqueta
                label = f"{class_name}: {conf:.2f}"
                label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
                cv2.rectangle(frame, (x1, y1 - 25), (x1 + label_size[0], y1), (0, 255, 0), -1)
                cv2.putText(frame, label, (x1, y1 - 5),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

        return frame, detections

    def run_webcam(self, camera_id=0, conf_threshold=0.5, show_fps=True):
        """Ejecuta detección en tiempo real desde webcam"""
        cap = cv2.VideoCapture(camera_id)

        if not cap.isOpened():
            print("[ERROR] No se pudo abrir la cámara")
            return

        print("[OK] Cámara abierta")
        print(f"[*] Presiona 'q' para salir")

        import time

        while True:
            ret, frame = cap.read()
            if not ret:
                print("[ERROR] Error leyendo frame")
                break

            frame = cv2.resize(frame, (640, 480))

            start_time = time.time()
            result, detections = self.detect_frame(frame, conf_threshold)
            inference_time = time.time() - start_time

            # Mostrar FPS e información
            if show_fps:
                fps = 1 / inference_time
                cv2.putText(result, f"FPS: {fps:.1f}", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(result, f"Objetos: {len(detections)}", (10, 70),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(result, f"Tiempo: {inference_time*1000:.1f}ms", (10, 110),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            cv2.imshow("YOLO Detección", result)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

    def run_video_file(self, video_path, conf_threshold=0.5, show_fps=True):
        """Ejecuta detección en archivo de video"""
        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            print(f"[ERROR] No se pudo abrir: {video_path}")
            return

        # Obtener información del video
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        print(f"[OK] Video abierto: {width}x{height} @ {fps} FPS ({total_frames} frames)")
        print("[*] Presiona 'q' para salir")

        frame_count = 0
        import time

        while True:
            ret, frame = cap.read()
            if not ret:
                print(f"[OK] Video finalizado ({frame_count}/{total_frames} frames)")
                break

            start_time = time.time()
            result, detections = self.detect_frame(frame, conf_threshold)
            inference_time = time.time() - start_time

            if show_fps:
                cv2.putText(result, f"FPS: {1/inference_time:.1f}", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(result, f"Frame: {frame_count}/{total_frames}", (10, 70),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(result, f"Objetos: {len(detections)}", (10, 110),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            cv2.imshow("YOLO Detección", result)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break

            frame_count += 1

        cap.release()
        cv2.destroyAllWindows()

def main():
    """Función principal"""
    print("=" * 70)
    print("Volumen 2 — Capítulo 2: OpenCV+YOLO — Detección YOLO v8")
    print("=" * 70)

    model_size = 'n'  # nano por defecto (rápido)
    if len(sys.argv) > 1:
        model_size = sys.argv[1]

    detector = YOLODetector(model_size)

    if len(sys.argv) > 2:
        # Ejecutar en archivo de video
        detector.run_video_file(sys.argv[2])
    else:
        # Ejecutar en webcam
        print("\n[*] Inicia detección desde webcam")
        detector.run_webcam()

if __name__ == "__main__":
    main()
