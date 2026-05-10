#!/usr/bin/env python3
"""
Volumen 2 — Capítulo 2: OpenCV — Detección de Color por HSV
Detecta colores específicos en video en tiempo real (webcam o archivo)
"""

import cv2
import numpy as np
import sys

class ColorDetector:
    """Detector de colores basado en HSV"""

    # Rangos HSV predefinidos (puedes ajustarlos)
    COLORS = {
        'red': {
            'lower1': np.array([0, 100, 100]),
            'upper1': np.array([10, 255, 255]),
            'lower2': np.array([170, 100, 100]),
            'upper2': np.array([180, 255, 255]),
            'bgr': (0, 0, 255)
        },
        'green': {
            'lower': np.array([50, 40, 40]),
            'upper': np.array([90, 255, 255]),
            'bgr': (0, 255, 0)
        },
        'blue': {
            'lower': np.array([100, 100, 100]),
            'upper': np.array([130, 255, 255]),
            'bgr': (255, 0, 0)
        },
        'yellow': {
            'lower': np.array([20, 100, 100]),
            'upper': np.array([40, 255, 255]),
            'bgr': (0, 255, 255)
        }
    }

    def __init__(self, color_name: str = 'red'):
        """Inicializa el detector para un color específico"""
        if color_name.lower() not in self.COLORS:
            raise ValueError(f"Color {color_name} no reconocido. Usar: {list(self.COLORS.keys())}")

        self.color_name = color_name.lower()
        self.color_config = self.COLORS[self.color_name]

    def detect_color(self, frame):
        """Detecta el color en un frame"""
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Crear máscara (algunos colores tienen dos rangos, como el rojo)
        if 'lower1' in self.color_config:
            mask1 = cv2.inRange(hsv, self.color_config['lower1'], self.color_config['upper1'])
            mask2 = cv2.inRange(hsv, self.color_config['lower2'], self.color_config['upper2'])
            mask = cv2.bitwise_or(mask1, mask2)
        else:
            mask = cv2.inRange(hsv, self.color_config['lower'], self.color_config['upper'])

        # Aplicar filtro morfológico para mejorar máscara
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        return mask

    def find_contours(self, mask):
        """Encuentra contornos en la máscara"""
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        return contours

    def process_frame(self, frame, show_mask=False):
        """Procesa un frame completo: detecta, dibuja rectángulos y contornos"""
        mask = self.detect_color(frame)
        contours = self.find_contours(mask)

        result = frame.copy()
        bgr_color = self.color_config['bgr']

        if contours:
            for contour in contours:
                area = cv2.contourArea(contour)

                # Filtrar contornos pequeños (ruido)
                if area > 500:
                    # Dibujar contorno
                    cv2.drawContours(result, [contour], 0, bgr_color, 2)

                    # Dibujar bounding box
                    x, y, w, h = cv2.boundingRect(contour)
                    cv2.rectangle(result, (x, y), (x + w, y + h), bgr_color, 2)

                    # Calcular centroide
                    M = cv2.moments(contour)
                    if M['m00'] > 0:
                        cx = int(M['m10'] / M['m00'])
                        cy = int(M['m01'] / M['m00'])
                        cv2.circle(result, (cx, cy), 5, bgr_color, -1)

        # Mostrar información
        cv2.putText(result, f"Color: {self.color_name.upper()}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(result, f"Objetos encontrados: {len([c for c in contours if cv2.contourArea(c) > 500])}",
                   (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        if show_mask:
            return result, mask
        return result

    def run_webcam(self, camera_id=0):
        """Ejecuta detección en tiempo real desde webcam"""
        cap = cv2.VideoCapture(camera_id)

        if not cap.isOpened():
            print("[ERROR] No se pudo abrir la cámara")
            return

        print(f"[OK] Cámara abierta. Presiona 'q' para salir")

        while True:
            ret, frame = cap.read()
            if not ret:
                print("[ERROR] Error leyendo frame")
                break

            frame = cv2.resize(frame, (640, 480))
            result, mask = self.process_frame(frame, show_mask=True)

            # Mostrar lado a lado
            cv2.imshow("Original", result)
            cv2.imshow("Máscara HSV", mask)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

    def run_video_file(self, video_path):
        """Ejecuta detección en archivo de video"""
        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            print(f"[ERROR] No se pudo abrir el video: {video_path}")
            return

        print(f"[OK] Video abierto. Presiona 'q' para salir")

        while True:
            ret, frame = cap.read()
            if not ret:
                print("[OK] Video finalizado")
                break

            result, mask = self.process_frame(frame, show_mask=True)

            cv2.imshow("Detección de Color", result)
            cv2.imshow("Máscara", mask)

            key = cv2.waitKey(30) & 0xFF
            if key == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

def main():
    """Función principal"""
    print("=" * 70)
    print("Volumen 2 — Capítulo 2: OpenCV — Detección de Color")
    print("=" * 70)

    color = 'red'
    if len(sys.argv) > 1:
        color = sys.argv[1]

    detector = ColorDetector(color)

    if len(sys.argv) > 2:
        # Ejecutar en archivo de video
        detector.run_video_file(sys.argv[2])
    else:
        # Ejecutar en webcam
        print(f"\n[*] Detectando color: {color.upper()}")
        print("[*] Presiona 'q' para salir")
        detector.run_webcam()

if __name__ == "__main__":
    main()
