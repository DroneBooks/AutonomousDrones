#!/usr/bin/env python3
"""
Volumen 1 — Anexo A2: Python — Ejemplo Avanzado — Telemetría + Visión en Paralelo
Combina lectura de telemetría MAVLink con detección de color OpenCV
usando threads para ejecutar ambos módulos simultáneamente.
"""

import cv2
import numpy as np
import threading
import time
import csv
from pymavlink import mavutil

# ─── Configuración global ───────────────────────────────────────────────────
CONNECTION_STRING = '127.0.0.1:14550'
CSV_LOG_FILE      = 'telemetry_vision_log.csv'
RUN_DURATION      = 60  # segundos de ejecución

# Variables compartidas entre threads (con bloqueo para seguridad)
lock = threading.Lock()
shared_data = {
    'altitude': 0.0,
    'battery':  0.0,
    'objects':  0,
    'running':  True,
}

# ─── Módulo de Telemetría ────────────────────────────────────────────────────

def telemetry_reader():
    """Lee telemetría del drone e imprime cada 500 ms."""
    print("[TELEMETRIA] Conectando...")

    try:
        mav = mavutil.mavlink_connection(CONNECTION_STRING, timeout=5)
        mav.wait_heartbeat(timeout=10)
        print("[TELEMETRIA] Conectado\n")
    except Exception as e:
        print(f"[TELEMETRIA] Error de conexion: {e}")
        print("[TELEMETRIA] Continuando sin drone (datos en 0)")
        while shared_data['running']:
            time.sleep(0.5)
        return

    while shared_data['running']:
        msg_gps = mav.recv_match(type='GPS_RAW_INT', timeout=0.5)
        if msg_gps:
            alt = msg_gps.alt / 1000.0

        msg_bat = mav.recv_match(type='BATTERY_STATUS', timeout=0.5)
        if msg_bat:
            voltage = msg_bat.voltage / 1000.0
        else:
            voltage = 0.0

        with lock:
            shared_data['altitude'] = alt if msg_gps else shared_data['altitude']
            shared_data['battery']  = voltage

        print(f"[TELEMETRIA] Alt={shared_data['altitude']:.1f}m  "
              f"Bat={shared_data['battery']:.2f}V  "
              f"Objetos_vision={shared_data['objects']}")

        time.sleep(0.5)

    mav.close()
    print("[TELEMETRIA] Conexion cerrada")


# ─── Módulo de Visión ────────────────────────────────────────────────────────

def vision_processor():
    """Detecta objetos rojos con OpenCV y actualiza el contador compartido."""
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("[VISION] No se pudo abrir la camara — modulo desactivado")
        while shared_data['running']:
            time.sleep(0.1)
        return

    print("[VISION] Camara abierta\n")

    lower_red1 = np.array([0,   100, 100])
    upper_red1 = np.array([10,  255, 255])
    lower_red2 = np.array([170, 100, 100])
    upper_red2 = np.array([180, 255, 255])

    prev_time = time.time()

    while shared_data['running']:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.resize(frame, (640, 480))
        hsv   = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        mask  = cv2.bitwise_or(mask1, mask2)

        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mask   = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(mask, cv2.RETR_TREE,
                                        cv2.CHAIN_APPROX_SIMPLE)
        count = sum(1 for c in contours if cv2.contourArea(c) > 500)

        with lock:
            shared_data['objects'] = count

        # FPS
        now  = time.time()
        fps  = 1.0 / max(now - prev_time, 1e-6)
        prev_time = now

        # Anotaciones en pantalla
        with lock:
            alt = shared_data['altitude']
            bat = shared_data['battery']

        cv2.putText(frame, f"Objetos rojos: {count}",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
        cv2.putText(frame, f"Alt: {alt:.1f}m  Bat: {bat:.2f}V",
                    (10, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 200, 0), 2)
        cv2.putText(frame, f"FPS: {fps:.1f}",
                    (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 255, 0), 2)
        cv2.putText(frame, "Presiona 'q' para salir",
                    (10, 460), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

        for c in contours:
            if cv2.contourArea(c) > 500:
                x, y, w, h = cv2.boundingRect(c)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

        cv2.imshow("Ejemplo Avanzado — Vision + Telemetria", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            with lock:
                shared_data['running'] = False
            break

    cap.release()
    cv2.destroyAllWindows()
    print("[VISION] Camara liberada")


# ─── Logger CSV ──────────────────────────────────────────────────────────────

def csv_logger():
    """Guarda un registro combinado de telemetría y visión en CSV."""
    with open(CSV_LOG_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'altitude_m', 'battery_v', 'red_objects'])

        while shared_data['running']:
            with lock:
                row = [
                    time.strftime('%H:%M:%S'),
                    shared_data['altitude'],
                    shared_data['battery'],
                    shared_data['objects'],
                ]
            writer.writerow(row)
            f.flush()
            time.sleep(1.0)

    print(f"[LOG] CSV guardado en {CSV_LOG_FILE}")


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("Volumen 1 — Anexo A2: Python — Ejemplo Avanzado")
    print("Telemetria MAVLink + Vision OpenCV en paralelo")
    print("=" * 60)
    print(f"Duracion maxima: {RUN_DURATION}s   Log: {CSV_LOG_FILE}\n")

    # Crear y arrancar threads
    t_telemetry = threading.Thread(target=telemetry_reader, daemon=True)
    t_vision    = threading.Thread(target=vision_processor, daemon=True)
    t_logger    = threading.Thread(target=csv_logger,       daemon=True)

    t_telemetry.start()
    t_vision.start()
    t_logger.start()

    # Esperar hasta que se cumpla el tiempo o el usuario salga con 'q'
    start = time.time()
    while shared_data['running'] and (time.time() - start) < RUN_DURATION:
        time.sleep(0.5)

    # Señal de parada
    with lock:
        shared_data['running'] = False

    t_telemetry.join(timeout=3)
    t_logger.join(timeout=3)

    print("\n[OK] Ejemplo avanzado finalizado")
    print(f"[OK] Datos guardados en {CSV_LOG_FILE}")


if __name__ == "__main__":
    main()
