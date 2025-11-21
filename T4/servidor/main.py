import socket
import sys
from thread_cliente import ThreadCliente
import threading
import json
from api import iniciar_api
from logica_aviator import PartidaAviator
from logica_blackjack import PartidaBlackjack


class Servidor:
    """
    Clase que representa un servidor distribuidor de archivos.
    En cuanto se instancia levanta un socket para escuchar potenciales
    clientes.
    """

    id_clientes = 0

    def __init__(self, port: int, host: str, api_port: int) -> None:
        """
        Inicializar el servidor.
        """
        self.host = host
        self.HOST = host # Alias para logica_aviator
        self.port = port
        self.API_PORT = api_port
        self.clientes = {}
        self.socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # ⚠️ CRÍTICO 1.2: Inicializar las instancias de juego
        self.salas = {
            "aviator": PartidaAviator(self), # Pasa 'self' para que la lógica de juego pueda usar el servidor
            "blackjack": PartidaBlackjack(self)
        }
        
    def bind_listen(self) -> None:
        """
        Método que conecta el servidor al host y port dado.
        """
        self.socket_server.bind((self.host, self.port))
        self.socket_server.listen()
        print(f"Servidor escuchando en {self.host} : {self.port}")

    def accept_connections_thread(self) -> None:
        """
        Función encargada de aceptar clientes y asignarles un Thread para su atención.
        """
        while True:
            socket_cliente, address = self.socket_server.accept()
            print(f"Nuevo cliente conectado: {socket_cliente} {address}")

            # Creamos nuestro "minion" encargado de escuchar exclusivamente al cliente.
            listening_client_thread = ThreadCliente(
                self.id_clientes, 
                socket_cliente, 
                address,
                self # ⚠️ CRÍTICO 2: Pasa la instancia del servidor a ThreadCliente
            )

            # Siempre se recomienda guardar la info del cliente para fácil acceso
            # (administrar clientes, cortar conexiones, etc.)
            self.clientes[self.id_clientes] = listening_client_thread

            self.id_clientes += 1
            listening_client_thread.start()


if __name__ == "__main__":
    # 1. Leer Parámetros de Conexión
    RUTA_CONEXION = "servidor/conexion.json" # Ajusta la ruta según tu estructura
    try:
        with open(RUTA_CONEXION, 'r') as file:
            datos_conexion = json.load(file)
            HOST = datos_conexion.get("host", "localhost")
            PORT = datos_conexion.get("puerto", 4444)
            API_PORT = datos_conexion.get("puertoAPI", 5555) # 👈 Puerto de la API
    except FileNotFoundError:
        print("Error: conexion.json no encontrado.")
        sys.exit()

    # 2. Iniciar la API en un hilo
    print(f"Iniciando API en {HOST}:{API_PORT}...")
    api_thread = threading.Thread(
        target=iniciar_api, 
        args=(HOST, API_PORT), 
        daemon=True
    )
    api_thread.start()

    # 3. Iniciar el Servidor de Sockets (Lógica existente)
    server = Servidor(PORT, HOST, API_PORT)
    server.bind_listen()
    
    try:
        server.accept_connections_thread()
    except KeyboardInterrupt:
        print("\nServidor detenido.")
    except Exception as e:
        print(f"Error fatal del servidor: {e}")