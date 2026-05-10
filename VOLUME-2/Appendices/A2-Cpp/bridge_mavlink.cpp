/*
 * bridge_mavlink.cpp — Puente MAVLink ↔ ROS2 (C++)
 *
 * Este nodo traduce entre:
 * - MAVLink: protocolo binario de Pixhawk (drones reales)
 * - ROS2 topics: tópicos estándar de ROS2 (sistema modular)
 *
 * Flujo:
 * Pixhawk (MAVLink) ← Serial o UDP → ROS2 Node ← ROS2 topics → Otros nodos
 *
 * Compilación:
 *   cd ~/ros2_ws && colcon build --packages-select drone_telemetry
 *
 * Ejecución (requiere Pixhawk conectado o SITL):
 *   source install/setup.bash
 *   ros2 run drone_telemetry bridge_mavlink --connect 127.0.0.1:14550
 *
 * Conceptos clave (del Anexo A2):
 * - Integración de bibliotecas externas (pymavlink en Python, pero aquí simulamos)
 * - Threading para lectura no-bloqueante
 * - Manejo de estructura binaria MAVLink
 * - Conversión entre tipos de datos
 * - Patrón Publisher-Subscriber para telemetría
 *
 * Nota educativa: Este es código de ejemplo. En producción, usar MAVROS ROS2:
 *   https://github.com/mavlink/mavros
 */

#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/float64.hpp"
#include "geometry_msgs/msg/twist.hpp"
#include <thread>
#include <cstring>
#include <cmath>

/*
 * Estructura simulada de mensaje MAVLink HEARTBEAT.
 * En el código real, esto vendría de pymavlink::msg.
 *
 * struct MAVLINK_MSG_HEARTBEAT {
 *     uint8_t type;              // Tipo de vehículo
 *     uint8_t autopilot;         // Tipo de autopilot
 *     uint8_t base_mode;         // Modo base
 *     uint32_t custom_mode;      // Modo personalizado
 *     uint8_t system_status;     // Estado del sistema
 *     uint8_t mavlink_version;   // Versión MAVLink
 * };
 */

class BridgeMavlinkROS2 : public rclcpp::Node {
public:
    BridgeMavlinkROS2() : Node("bridge_mavlink"),
                          conectado_(false),
                          contador_heartbeat_(0) {
        /*
         * Publishers ROS2: traducir datos MAVLink a tópicos ROS2.
         * Estos tópicos pueden ser escuchados por otros nodos.
         */
        pub_altitud_ = create_publisher<std_msgs::msg::Float64>(
            "/mavlink/altitud", 10);
        pub_velocidad_ = create_publisher<std_msgs::msg::Float64>(
            "/mavlink/velocidad", 10);
        pub_bateria_ = create_publisher<std_msgs::msg::Float64>(
            "/mavlink/bateria", 10);
        pub_yaw_ = create_publisher<std_msgs::msg::Float64>(
            "/mavlink/yaw", 10);

        /*
         * Subscriber ROS2: recibir comandos de control y enviarlos a MAVLink.
         * Los comandos de otros nodos (ej: planeador de trayectoria)
         * se convierten a comandos MAVLink para Pixhawk.
         */
        sub_cmd_vel_ = create_subscription<geometry_msgs::msg::Twist>(
            "/cmd_vel", 10,
            std::bind(&BridgeMavlinkROS2::callback_cmd_vel, this,
                      std::placeholders::_1));

        /*
         * Timer para heartbeat (latido del nodo).
         * En MAVLink, el heartbeat es un ping periódico hacia Pixhawk.
         */
        timer_heartbeat_ = create_wall_timer(
            std::chrono::milliseconds(1000),
            std::bind(&BridgeMavlinkROS2::callback_heartbeat, this));

        RCLCPP_INFO(get_logger(),
                    "✅ Bridge MAVLink-ROS2 iniciado");
        RCLCPP_INFO(get_logger(),
                    "   Publishers: /mavlink/{altitud,velocidad,bateria,yaw}");
        RCLCPP_INFO(get_logger(),
                    "   Subscriber: /cmd_vel para control de dron");
    }

    /*
     * Iniciar conexión a Pixhawk (simulado).
     * En el código real, esto usaría:
     *   - Serial: /dev/ttyUSB0 (Linux)
     *   - UDP: 127.0.0.1:14550 (SITL)
     */
    bool conectar(const std::string& puerto) {
        RCLCPP_INFO(get_logger(), "🔌 Intentando conectar a: %s", puerto.c_str());

        // En versión educativa, simulamos conexión exitosa.
        // Código real: socket UDP o puerto serial.
        conectado_ = true;
        contador_heartbeat_ = 0;

        RCLCPP_INFO(get_logger(), "✅ Conexión establecida");
        return true;
    }

private:
    /*
     * Callback periódico: enviar heartbeat a Pixhawk y simular telemetría.
     * El heartbeat es obligatorio en MAVLink (latido periódico).
     */
    void callback_heartbeat() {
        if (!conectado_) {
            RCLCPP_WARN_THROTTLE(get_logger(), *get_clock(), 5000,
                                 "⚠️  No conectado a Pixhawk");
            return;
        }

        contador_heartbeat_++;

        // Simular datos de Pixhawk (en código real, leer de UART/UDP)
        simular_telemetria();

        // Log cada 10 ciclos (cada 10 segundos)
        if (contador_heartbeat_ % 10 == 0) {
            RCLCPP_INFO(get_logger(),
                        "💓 Heartbeat #%d — telemetría publicada",
                        contador_heartbeat_);
        }
    }

    /*
     * Simular datos de Pixhawk para demostración.
     * En código real, estos valores vendrían de MAVLink ATTITUDE y GPS_RAW.
     */
    void simular_telemetria() {
        // Crear datos simulados (varían con el tiempo)
        double t = contador_heartbeat_ * 0.1;
        double altitud = 15.0 + 5.0 * std::sin(t);
        double velocidad = 5.0 + 2.0 * std::cos(t * 0.5);
        double bateria = 100.0 - (contador_heartbeat_ * 0.5);
        double yaw = std::fmod(t * 10, 360.0);  // Girar constantemente

        // Limitar batería a [0, 100]
        if (bateria < 0) bateria = 0;

        // Publicar en tópicos ROS2
        auto msg_alt = std_msgs::msg::Float64();
        msg_alt.data = altitud;
        pub_altitud_->publish(msg_alt);

        auto msg_vel = std_msgs::msg::Float64();
        msg_vel.data = velocidad;
        pub_velocidad_->publish(msg_vel);

        auto msg_bat = std_msgs::msg::Float64();
        msg_bat.data = bateria;
        pub_bateria_->publish(msg_bat);

        auto msg_yaw = std_msgs::msg::Float64();
        msg_yaw.data = yaw;
        pub_yaw_->publish(msg_yaw);
    }

    /*
     * Callback: recibir comando de control desde ROS2.
     * Estos comandos proceden del navegador / controlador de trayectoria.
     *
     * geometry_msgs/Twist contiene:
     * - linear: velocidad lineal (x, y, z) en m/s
     * - angular: velocidad angular (roll, pitch, yaw) en rad/s
     */
    void callback_cmd_vel(const geometry_msgs::msg::Twist::SharedPtr msg) {
        if (!conectado_) {
            RCLCPP_ERROR(get_logger(),
                         "❌ Ignorando comando: no conectado a Pixhawk");
            return;
        }

        /*
         * Convertir comando ROS2 a comando MAVLink SET_POSITION_TARGET_LOCAL_NED.
         * En código real, esto compilaría un paquete MAVLink y lo enviaría al dron.
         */
        double vx = msg->linear.x;     // Velocidad adelante (m/s)
        double vy = msg->linear.y;     // Velocidad lateral (m/s)
        double vz = msg->linear.z;     // Velocidad vertical (m/s)
        double yaw_rate = msg->angular.z;  // Velocidad de giro (rad/s)

        RCLCPP_INFO(get_logger(),
                    "📤 Comando ROS2 → MAVLink: vx=%.2f, vy=%.2f, vz=%.2f, "
                    "yaw_rate=%.2f",
                    vx, vy, vz, yaw_rate);

        // En código real:
        // mavlink_msg_set_position_target_local_ned_pack(...);
        // enviar_por_uart_o_udp(...);
    }

public:
    /*
     * Método: desconectar de Pixhawk.
     * En código real, cerraría puerto serial o socket UDP.
     */
    void desconectar() {
        if (conectado_) {
            RCLCPP_INFO(get_logger(), "🔓 Desconectando de Pixhawk...");
            conectado_ = false;
        }
    }

    bool esta_conectado() const { return conectado_; }

private:
    // Publishers (MAVLink → ROS2)
    rclcpp::Publisher<std_msgs::msg::Float64>::SharedPtr pub_altitud_;
    rclcpp::Publisher<std_msgs::msg::Float64>::SharedPtr pub_velocidad_;
    rclcpp::Publisher<std_msgs::msg::Float64>::SharedPtr pub_bateria_;
    rclcpp::Publisher<std_msgs::msg::Float64>::SharedPtr pub_yaw_;

    // Subscriber (ROS2 → MAVLink)
    rclcpp::Subscription<geometry_msgs::msg::Twist>::SharedPtr sub_cmd_vel_;

    // Timer para heartbeat
    rclcpp::TimerBase::SharedPtr timer_heartbeat_;

    // Estado de conexión
    bool conectado_;
    int contador_heartbeat_;
};

int main(int argc, char* argv[]) {
    rclcpp::init(argc, argv);

    auto nodo = std::make_shared<BridgeMavlinkROS2>();

    /*
     * Procesar argumentos de línea de comandos.
     * Ejemplo: ros2 run drone_telemetry bridge_mavlink --connect 127.0.0.1:14550
     */
    std::string puerto = "127.0.0.1:14550";  // SITL por defecto
    if (argc > 2 && std::string(argv[1]) == "--connect") {
        puerto = argv[2];
    }

    // Intentar conectar a Pixhawk
    if (!nodo->conectar(puerto)) {
        RCLCPP_ERROR(rclcpp::get_logger("rclcpp"),
                     "❌ No se pudo conectar a: %s", puerto.c_str());
        rclcpp::shutdown();
        return 1;
    }

    // Ejecutar: procesa callbacks y eventos
    rclcpp::spin(nodo);

    // Limpieza
    nodo->desconectar();
    rclcpp::shutdown();
    return 0;
}
