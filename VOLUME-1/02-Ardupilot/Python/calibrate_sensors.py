#!/usr/bin/env python3
"""
Volumen 1 — Capítulo 2: Ardupilot — Asistente de Calibración
Proporciona una guía interactiva para calibrar sensores del FC
"""

import sys

class CalibrationGuide:
    """Guía de calibración de sensores del Flight Controller"""

    def __init__(self):
        self.steps_completed = []

    def print_header(self, title):
        """Imprime un encabezado formateado"""
        print(f"\n{'='*70}")
        print(f"  {title}")
        print(f"{'='*70}\n")

    def print_step(self, step_num, title):
        """Imprime el título de un paso"""
        print(f"[PASO {step_num}] {title}")
        print("-" * 70)

    def step_1_compass(self):
        """Paso 1: Calibración de Brújula/Magnetómetro"""
        self.print_step(1, "Calibración de Brújula (Magnetómetro)")

        instructions = """
1. Conecta la batería principal (o USB si es necesario)
2. En QGroundControl o Mission Planner, ve a: Configuración > Sensores
3. Selecciona "Calibración de Brújula"
4. IMPORTANTE: Mantén el drone ALEJADO de objetos metálicos
5. Rota el drone suavemente en todas las direcciones:
   - Movimientos circulares (8 figuras)
   - Rotación en los 3 ejes: roll, pitch, yaw
   - Toma 60-90 segundos aproximadamente
6. Cuando termines, el software confirma "Calibración completada"

⚠️  ERRORES COMUNES:
   - Brújula desalineada: Resetea y reinicia
   - Interferencia electromagnética: Aleja el drone de cables/motores
   - No cubras el sensor: Deja espacios de aire alrededor
        """
        print(instructions)

        input("Presiona ENTER cuando hayas completado este paso...")
        self.steps_completed.append(1)
        print("[OK] Paso 1 completado\n")

    def step_2_accelerometer(self):
        """Paso 2: Calibración de Acelerómetro"""
        self.print_step(2, "Calibración de Acelerómetro (IMU)")

        instructions = """
1. El drone DEBE estar en una superficie PERFECTAMENTE PLANA
   - Usa un nivel de burbuja para verificar
   - Coloca el drone sobre una mesa firme
2. En QGroundControl/Mission Planner: Configuración > Sensores
3. Selecciona "Calibración de Acelerómetro"
4. Selecciona orientación: Generalmente "Roll=0, Pitch=0, Yaw=0" (plano)
5. Deja quieto el drone durante el proceso (15-30 segundos)
6. No toques ni muevas el drone hasta que terminen los 6 puntos

⚠️  ERRORES COMUNES:
   - Drone inclinado: Usa nivel, no adivines
   - Vibraciones: Asegura que la mesa esté firme
   - Cable USB suelto: Asegura bien la conexión
        """
        print(instructions)

        input("Presiona ENTER cuando hayas completado este paso...")
        self.steps_completed.append(2)
        print("[OK] Paso 2 completado\n")

    def step_3_radio(self):
        """Paso 3: Calibración de Radio Control"""
        self.print_step(3, "Calibración de Radio Control (RC)")

        instructions = """
1. ASEGÚRATE de que el drone esté SIN HÉLICES
   (¡MUY IMPORTANTE para seguridad!)
2. Enciende el transmisor ANTES de alimentar el FC
3. En QGroundControl/Mission Planner: Configuración > Radio
4. Presiona "Calibrar" y sigue los pasos:
   - Mueve cada palanca/switch a sus posiciones extremas
   - Izquierda/Derecha, Adelante/Atrás, Arriba/Abajo
   - Activa todos los switches y botones
5. El software registra los valores mín/máx de cada canal

⚠️  IMPORTANTE:
   - SIN HÉLICES durante esta calibración
   - Si necesitas resetear: Desconecta la batería
   - Verifica que todos los canales respondan correctamente
        """
        print(instructions)

        input("Presiona ENTER cuando hayas completado este paso...")
        self.steps_completed.append(3)
        print("[OK] Paso 3 completado\n")

    def step_4_esc(self):
        """Paso 4: Calibración de ESC"""
        self.print_step(4, "Calibración de ESC (Variador de Velocidad)")

        instructions = """
1. ASEGÚRATE de que NO HAY HÉLICES
2. Opciones:

   OPCIÓN A: Calibración de Rango (Recomendado para Ardupilot)
   - Desconecta la batería
   - Desconecta todos los ESCs del FC
   - Conecta SOLO UN ESC al canal 3 (Throttle) en el FC
   - Enciende el transmisor
   - Conecta la batería
   - El ESC debería emitir 2 bips
   - Mueve el throttle al máximo
   - El ESC emite 1 bip (señal calibrada)
   - Mueve throttle al mínimo
   - Repite para cada ESC

   OPCIÓN B: A través de Mission Planner
   - Ve a: Configuración > Prueba del Motor
   - Permite calibración automática de ESC
   - Sigue las instrucciones en pantalla

⚠️  SEGURIDAD:
   - NUNCA calibres con hélices instaladas
   - Verifica cada ESC responda al throttle
   - Si un ESC no responde: Resetea y reinicia
        """
        print(instructions)

        input("Presiona ENTER cuando hayas completado este paso...")
        self.steps_completed.append(4)
        print("[OK] Paso 4 completado\n")

    def step_5_verification(self):
        """Paso 5: Verificación Final"""
        self.print_step(5, "Verificación Final")

        checks = """
LISTA DE VERIFICACIÓN ANTES DE VOLAR:

□ Brújula calibrada (sin errores en logs)
□ Acelerómetro calibrado (nivel perfecto usado)
□ Radio calibrada (todos los canales responden)
□ ESCs calibrados (responden al throttle)
□ Hélices INSTALADAS correctamente
□ Batería totalmente cargada
□ Controles de la radio funcionan
□ No hay vibraciones visibles
□ Drone está equilibrado
□ GPS tiene señal (si aplica)

DESPUÉS DE VERIFICAR TODO:
✓ El drone está LISTO para primer vuelo
✓ Inicia en modo "Stabilize" o "Altitude Hold"
✓ Vuela en zona abierta y despejada
✓ Mantén distancia de observadores
        """
        print(checks)

        input("Presiona ENTER cuando hayas completado este paso...")
        self.steps_completed.append(5)
        print("[OK] Paso 5 completado\n")

    def print_summary(self):
        """Imprime resumen de calibración"""
        self.print_header("RESUMEN DE CALIBRACIÓN")

        print(f"Pasos completados: {len(self.steps_completed)}/5\n")

        steps_names = {
            1: "Brújula/Magnetómetro",
            2: "Acelerómetro (IMU)",
            3: "Radio Control",
            4: "ESC (Variadores)",
            5: "Verificación Final"
        }

        for i in range(1, 6):
            status = "✓" if i in self.steps_completed else "✗"
            print(f"{status} Paso {i}: {steps_names[i]}")

        print("\n" + "="*70)

        if len(self.steps_completed) == 5:
            print("🎉 ¡CALIBRACIÓN COMPLETA!")
            print("Tu drone está listo para volar")
        else:
            print(f"⚠️  Faltan {5 - len(self.steps_completed)} pasos")

        print("="*70 + "\n")

    def run_wizard(self):
        """Ejecuta el asistente completo de calibración"""
        self.print_header("ASISTENTE DE CALIBRACIÓN - Ardupilot")

        print("""
Este asistente te guiará a través de toda la calibración
necesaria para volar tu drone con Ardupilot de forma segura.

REQUISITOS:
- Flight Controller (Pixhawk, Pixhawk Mini, etc.)
- QGroundControl o Mission Planner instalado
- Batería completamente cargada
- Transmisor RC programado
- Drone EN UNA MESA PLANA (no sostengas)

⚠️  SEGURIDAD: Los pasos especifican cuándo NO tener hélices
        """)

        input("Presiona ENTER para comenzar...")

        try:
            self.step_1_compass()
            self.step_2_accelerometer()
            self.step_3_radio()
            self.step_4_esc()
            self.step_5_verification()
            self.print_summary()

        except KeyboardInterrupt:
            print("\n\n[*] Calibración interrumpida por usuario")
            self.print_summary()

def main():
    """Función principal"""
    guide = CalibrationGuide()
    guide.run_wizard()

if __name__ == "__main__":
    main()
