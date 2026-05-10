#!/bin/bash
# install_ros2.sh — Instalación automatizada de ROS2 Humble + MAVROS + Nav2
# Requisito: Ubuntu 22.04 LTS con acceso sudo
# Uso: chmod +x install_ros2.sh && ./install_ros2.sh

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log()    { echo -e "${GREEN}[OK]${NC} $1"; }
warn()   { echo -e "${YELLOW}[AVISO]${NC} $1"; }
error()  { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# --- Verificaciones previas ---

if [[ "$EUID" -eq 0 ]]; then
    error "No ejecutes este script como root. Usa tu usuario normal (con sudo disponible)."
fi

if ! grep -q "22.04" /etc/os-release 2>/dev/null; then
    warn "Este script está diseñado para Ubuntu 22.04. Otras versiones pueden fallar."
fi

echo ""
echo "=========================================="
echo "  DroneAcademy — Instalación ROS2 Humble"
echo "=========================================="
echo ""
log "Sistema verificado. Iniciando instalación..."
echo ""

# --- Paso 1: Repositorio ROS2 ---

log "Paso 1/6: Configurando repositorio ROS2..."

sudo apt update -q
sudo apt install -y -q software-properties-common curl gnupg lsb-release

sudo add-apt-repository universe -y

sudo curl -sSL https://repo.ros2.org/ros.key \
    -o /usr/share/keyrings/ros-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] \
http://packages.ros.org/ros2/ubuntu $(source /etc/os-release && echo $UBUNTU_CODENAME) main" \
    | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

sudo apt update -q
log "Repositorio ROS2 configurado."

# --- Paso 2: ROS2 Humble Desktop ---

log "Paso 2/6: Instalando ROS2 Humble Desktop (~1.5 GB, puede tardar varios minutos)..."

sudo apt install -y -q ros-humble-desktop

log "ROS2 Humble Desktop instalado."

# --- Paso 3: Herramientas de desarrollo ---

log "Paso 3/6: Instalando herramientas de desarrollo..."

sudo apt install -y -q \
    build-essential \
    cmake \
    git \
    python3-colcon-common-extensions \
    python3-rosdep2 \
    python3-pip \
    python3-argcomplete

pip3 install --quiet MAVProxy

log "Herramientas de desarrollo instaladas."

# --- Paso 4: MAVROS + Nav2 ---

log "Paso 4/6: Instalando MAVROS y Nav2..."

sudo apt install -y -q \
    ros-humble-mavros \
    ros-humble-mavros-msgs \
    ros-humble-geographic-msgs \
    ros-humble-nav2-bringup \
    ros-humble-nav2-core \
    ros-humble-navigation2 \
    ros-humble-slam-toolbox

# Datos geográficos requeridos por MAVROS
sudo /opt/ros/humble/lib/mavros/install_geographiclib_datasets.sh 2>/dev/null || \
    warn "install_geographiclib_datasets falló (puede ignorarse si ya están instalados)."

log "MAVROS y Nav2 instalados."

# --- Paso 5: Gazebo (simulación) ---

log "Paso 5/6: Instalando Gazebo Classic..."

sudo apt install -y -q gazebo ros-humble-gazebo-ros-pkgs

log "Gazebo instalado."

# --- Paso 6: Configurar entorno en .bashrc ---

log "Paso 6/6: Configurando entorno en ~/.bashrc..."

BASHRC="$HOME/.bashrc"
SOURCE_LINE="source /opt/ros/humble/setup.bash"
DOMAIN_LINE="export ROS_DOMAIN_ID=0"
LOCALHOST_LINE="export ROS_LOCALHOST_ONLY=0"

# Añadir solo si no existe ya
grep -qxF "$SOURCE_LINE"   "$BASHRC" || echo "$SOURCE_LINE"   >> "$BASHRC"
grep -qxF "$DOMAIN_LINE"   "$BASHRC" || echo "$DOMAIN_LINE"   >> "$BASHRC"
grep -qxF "$LOCALHOST_LINE" "$BASHRC" || echo "$LOCALHOST_LINE" >> "$BASHRC"

log "Entorno configurado en ~/.bashrc"

# --- Verificación final ---

echo ""
echo "=========================================="
echo "  Verificando instalación..."
echo "=========================================="

source /opt/ros/humble/setup.bash

ROS_VER=$(ros2 --version 2>/dev/null || echo "no encontrado")
log "Versión ROS2: $ROS_VER"

PKG_COUNT=$(ros2 pkg list 2>/dev/null | wc -l)
log "Paquetes disponibles: $PKG_COUNT"

echo ""
echo "=========================================="
echo "  ¡Instalación completada!"
echo "=========================================="
echo ""
echo "  Próximos pasos:"
echo "  1. Reinicia la terminal (o ejecuta: source ~/.bashrc)"
echo "  2. Verifica con: ros2 run demo_nodes_cpp talker"
echo "  3. En otra terminal: ros2 run demo_nodes_cpp listener"
echo ""
