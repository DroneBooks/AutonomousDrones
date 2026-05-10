#!/usr/bin/env python3
"""
Conversión de modelos YOLO a TensorRT para Jetson.

Este script demuestra cómo optimizar modelos YOLO v8 usando TensorRT,
un motor de inferencia de NVIDIA que acelera 2-10x sin pérdida de precisión.

Uso:
    python jetson_yolo_optimization.py --model yolov8n.pt
    python jetson_yolo_optimization.py --model yolov8m.pt --device 0
    python jetson_yolo_optimization.py --model custom.pt --workspace 4

Requisitos:
    - Ubuntu 22.04 o JetPack 5.1+ (si usas Jetson)
    - NVIDIA CUDA 11.8+ (instalado automáticamente en Jetson)
    - PyTorch con CUDA support
    - ultralytics (YOLO v8)
"""

import argparse
import time
import os
from pathlib import Path
import numpy as np

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    print("⚠️  PyTorch no instalado. Instala con: pip install torch torchvision")

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    print("⚠️  Ultralytics no instalada. Instala con: pip install ultralytics")


def check_hardware():
    """Detecta si CUDA está disponible y qué GPU se usa."""
    if not TORCH_AVAILABLE:
        return False, "CPU (PyTorch no disponible)"

    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
        return True, f"{gpu_name} ({gpu_memory:.1f} GB)"

    return False, "CPU (CUDA no detectada)"


def convert_to_tensorrt(model_path, device=0, workspace=2):
    """
    Convierte un modelo YOLO a TensorRT.

    Args:
        model_path (str): Ruta del modelo .pt de YOLO
        device (int): GPU a usar (0 = primera GPU)
        workspace (int): MB de workspace para TensorRT (mayor = más rápido pero más memoria)

    Returns:
        Path: Ruta del modelo convertido (.engine)
    """
    if not YOLO_AVAILABLE:
        print("❌ Ultralytics no disponible. No se puede convertir.")
        return None

    if not os.path.exists(model_path):
        print(f"❌ Modelo no encontrado: {model_path}")
        return None

    print(f"\n📦 Convirtiendo {Path(model_path).name} a TensorRT...")
    print(f"   Dispositivo: GPU {device}")
    print(f"   Workspace: {workspace} MB")

    try:
        model = YOLO(model_path)

        # Exportar a formato TensorRT
        export_path = model.export(
            format='engine',
            device=device,
            half=True,  # Usar float16 para ahorrar memoria y mejorar velocidad
            workspace=workspace,
            verbose=False
        )

        print(f"✅ Conversión completada: {export_path}")
        return Path(export_path)

    except Exception as e:
        print(f"❌ Error durante conversión: {e}")
        return None


def get_model_size(model_path):
    """Obtiene el tamaño del archivo del modelo en MB."""
    return os.path.getsize(model_path) / (1024 * 1024)


def benchmark_inference(model_path, format_name, num_iterations=100):
    """
    Mide la latencia de inferencia de un modelo.

    Args:
        model_path (str): Ruta del modelo (.pt o .engine)
        format_name (str): Nombre del formato (ej: "YOLO PyTorch", "TensorRT")
        num_iterations (int): Número de inferencias a ejecutar

    Returns:
        dict: Estadísticas de latencia (mean, min, max, std)
    """
    if not YOLO_AVAILABLE:
        return None

    try:
        model = YOLO(model_path)

        # Crear imagen dummy (640x640 es estándar para YOLO)
        dummy_image = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)

        # Calentar la GPU (primera inferencia es más lenta)
        model(dummy_image, verbose=False)

        print(f"\n⏱️  Midiendo latencia de {format_name}...")
        print(f"   Iteraciones: {num_iterations}")

        latencies = []

        for i in range(num_iterations):
            start = time.perf_counter()
            model(dummy_image, verbose=False)
            end = time.perf_counter()

            latencies.append((end - start) * 1000)  # Convertir a ms

            if (i + 1) % 20 == 0:
                print(f"   {i + 1}/{num_iterations} completadas...", end='\r')

        print(f"   {num_iterations}/{num_iterations} completadas!    ")

        return {
            'format': format_name,
            'mean': np.mean(latencies),
            'min': np.min(latencies),
            'max': np.max(latencies),
            'std': np.std(latencies),
            'p50': np.percentile(latencies, 50),
            'p95': np.percentile(latencies, 95),
        }

    except Exception as e:
        print(f"❌ Error durante benchmark: {e}")
        return None


def print_stats(pytorch_stats, tensorrt_stats):
    """Imprime comparativa de stats entre formatos."""
    print("\n" + "="*70)
    print("📊 RESULTADOS DE OPTIMIZACIÓN")
    print("="*70)

    if pytorch_stats:
        print(f"\n🔹 {pytorch_stats['format']}:")
        print(f"   Latencia media:  {pytorch_stats['mean']:.2f} ms")
        print(f"   Latencia min:    {pytorch_stats['min']:.2f} ms")
        print(f"   Latencia max:    {pytorch_stats['max']:.2f} ms")
        print(f"   Percentil 95:    {pytorch_stats['p95']:.2f} ms")
        print(f"   Desv. estándar:  {pytorch_stats['std']:.2f} ms")

    if tensorrt_stats:
        print(f"\n🟢 {tensorrt_stats['format']}:")
        print(f"   Latencia media:  {tensorrt_stats['mean']:.2f} ms")
        print(f"   Latencia min:    {tensorrt_stats['min']:.2f} ms")
        print(f"   Latencia max:    {tensorrt_stats['max']:.2f} ms")
        print(f"   Percentil 95:    {tensorrt_stats['p95']:.2f} ms")
        print(f"   Desv. estándar:  {tensorrt_stats['std']:.2f} ms")

    if pytorch_stats and tensorrt_stats:
        speedup = pytorch_stats['mean'] / tensorrt_stats['mean']
        print(f"\n⚡ Aceleración: {speedup:.1f}x más rápido")
        print(f"   Mejora de latencia: {(1 - tensorrt_stats['mean']/pytorch_stats['mean'])*100:.1f}%")

    print("="*70)


def main():
    parser = argparse.ArgumentParser(
        description='Convertir YOLO a TensorRT y medir mejoras de latencia.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python jetson_yolo_optimization.py --model yolov8n.pt
  python jetson_yolo_optimization.py --model yolov8m.pt --device 0 --workspace 4
  python jetson_yolo_optimization.py --model custom.pt --benchmark-only
        """
    )

    parser.add_argument('--model', type=str, default='yolov8n.pt',
                       help='Modelo YOLO a convertir (default: yolov8n.pt)')
    parser.add_argument('--device', type=int, default=0,
                       help='GPU a usar (default: 0)')
    parser.add_argument('--workspace', type=int, default=2,
                       help='MB workspace para TensorRT (default: 2)')
    parser.add_argument('--benchmark-only', action='store_true',
                       help='Solo hacer benchmark sin convertir')
    parser.add_argument('--iterations', type=int, default=100,
                       help='Iteraciones para benchmark (default: 100)')

    args = parser.parse_args()

    # Detectar hardware
    cuda_available, gpu_info = check_hardware()
    print(f"\n📱 Hardware detectado: {gpu_info}")

    if not cuda_available and not args.benchmark_only:
        print("⚠️  CUDA no disponible. Puedes usar CPU pero será mucho más lento.")

    # Paso 1: Convertir a TensorRT (si no es benchmark-only)
    tensorrt_path = None
    if not args.benchmark_only:
        tensorrt_path = convert_to_tensorrt(args.model, args.device, args.workspace)

    # Paso 2: Comparar latencia
    pytorch_stats = benchmark_inference(
        args.model,
        "YOLO PyTorch",
        args.iterations
    )

    tensorrt_stats = None
    if tensorrt_path:
        tensorrt_stats = benchmark_inference(
            str(tensorrt_path),
            "YOLO TensorRT",
            args.iterations
        )

    # Paso 3: Mostrar resultados
    print_stats(pytorch_stats, tensorrt_stats)

    # Guardar modelo TensorRT ubicación
    if tensorrt_path:
        print(f"\n💾 Modelo optimizado guardado en:")
        print(f"   {tensorrt_path}")
        print(f"\n   Para usarlo en inferencia:")
        print(f"   model = YOLO('{tensorrt_path}')")


if __name__ == '__main__':
    main()
