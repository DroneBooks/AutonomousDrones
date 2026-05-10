#!/usr/bin/env python3
"""
Volumen 1 — Anexo A2: Python — Detección de Color Rojo
Script simple de OpenCV que detecta objetos rojos en tiempo real
"""

import cv2
import numpy as np

def main():
    """Función principal"""
    print("=" * 60)
    print("Volumen 1 — Anexo A2: Python — Detección de Color")
    print("=" * 60)

    # Abrir la cámara
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("[ERROR] No se pudo abrir la cámara")
        return

    print("[OK] Cámara abierta")
    print("[*] Detectando color ROJO. Presiona 'q' para salir\n")

    # Rangos HSV para detectar el color ROJO
    # Rojo tiene dos rangos porque está en los extremos del espectro HSV
    lower_red1 = np.array([0, 100, 100])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 100, 100])
    upper_red2 = np.array([180, 255, 255])

    while True:
        # Capturar un frame
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Error leyendo frame")
            break

        # Redimensionar para que sea más rápido
        frame = cv2.resize(frame, (640, 480))

        # Convertir de BGR a HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Crear máscaras para el rojo (dos rangos)
        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        mask = cv2.bitwise_or(mask1, mask2)

        # Aplicar morfología para mejorar la máscara
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        # Encontrar contornos (objetos rojos)
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Contar objetos detectados
        objeto_count = 0

        for contour in contours:
            area = cv2.contourArea(contour)

            # Filtrar contornos pequeños (ruido)
            if area > 500:
                objeto_count += 1

                # Dibujar contorno
                cv2.drawContours(frame, [contour], 0, (0, 0, 255), 2)

                # Dibujar bounding box
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

                # Dibujar centroide
                M = cv2.moments(contour)
                if M['m00'] > 0:
                    cx = int(M['m10'] / M['m00'])
                    cy = int(M['m01'] / M['m00'])
                    cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)
                    cv2.putText(frame, f"({cx}, {cy})", (cx + 10, cy),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        # Mostrar información
        cv2.putText(frame, f"Objetos ROJOS detectados: {objeto_count}",
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.putText(frame, "Presiona 'q' para salir",
                   (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        # Mostrar frames
        cv2.imshow("Detección de Color - Original", frame)
        cv2.imshow("Detección de Color - Máscara", mask)

        # Salir si presionas 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Liberar recursos
    cap.release()
    cv2.destroyAllWindows()
    print("\n[OK] Programa finalizado")

if __name__ == "__main__":
    main()
