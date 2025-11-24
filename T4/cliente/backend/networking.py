import socket
import json
from PyQt5.QtCore import QThread, pyqtSignal
from math import ceil
import parametros as para
import protocolo as pr

class Cliente(QThread):
    
    senal_respuesta_login = pyqtSignal(bool,str)
    senal_mostrar_principal = pyqtSignal(int)
    senal_actualizar_saldo = pyqtSignal(int)
    senal_actualizar_juego = pyqtSignal(dict)

    def __init__(self) -> None:
        """
        Inicializador de la clase y entabla conexión con el servidor.
        """
        super().__init__()
        
        ruta_json = "cliente/backend/conexion.json"
        with open(ruta_json, "r") as file:
            datos_conexion = json.load(file)
            self.port = datos_conexion["puerto"]
            self.host = datos_conexion["host"]

        self.chunk_size = 2**16
        self.buffer_size = 2**16

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Vamos a tratar de conectarnos. Si no funciona
        # cerramos todo
        
        try:
            self.socket.connect((self.host, self.port))
            print("[BACK] Conectado correctamente al servidor.")

        except ConnectionError:
            print("[BACK] No se logró conectar")
            self.socket.close()
            exit()

    def recibir_bytes(self, cantidad: int) -> bytearray:
        """
        Recibe N cantidad de bytes, los concatena y retorna como un
        único bytearray. [Mismo código de la EX4]
        """
        bytes_leidos = bytearray()
        while len(bytes_leidos) < cantidad:
            cantidad_restante = cantidad - len(bytes_leidos)
            bytes_leer = min(self.buffer_size, cantidad_restante)
            # Importante recv(N) va a leer hasta N bytes que le manden. Si le mandan
            # menos, por ejemplo, K (con K < N) entonces respuesta será de largo K
            respuesta = self.socket.recv(bytes_leer)
            bytes_leidos += respuesta
        return bytes_leidos

    # dentro de Cliente(QThread)
    def run(self) -> None:
        # ...
        while True:
            try:
                # 1. RECIBIR LARGO (4 bytes LITTLE ENDIAN)
                largo_bytes = self.recibir_bytes(4)
                if not largo_bytes: # Si no se reciben bytes, la conexión está cerrada.
                    raise ConnectionResetError("Conexión perdida con el servidor.")
                largo_contenido = int.from_bytes(largo_bytes, "little")

                num_paquetes = ceil(largo_contenido / para.CHUNK_SIZE)
                paquetes_recibidos = {}

                # 2. RECIBIR PAQUETES (128 bytes cada uno)
                for _ in range(num_paquetes):
                    paquete_encriptado = self.recibir_bytes(para.CHUNK_SIZE + 4) # 128 bytes
                    
                    # Desencriptar usando pr.cifrar_xor (porque empaquetar_mensaje no se usa aquí)
                    paquete = pr.cifrar_xor(paquete_encriptado)

                    # Obtener Índice (4 bytes BIG ENDIAN)
                    indice = int.from_bytes(paquete[:4], "big")
                    
                    # Obtener Contenido (124 bytes)
                    chunk = paquete[4:]
                    
                    paquetes_recibidos[indice] = chunk

                # 3. REASAMBLAR CONTENIDO (Usando helper)
                # Ojo: desencriptar_y_reasamblar no hace XOR, solo reensambla.
                # Ya hicimos el XOR arriba.
                
                # Pero pr.desencriptar_y_reasamblar hace JSON loads.
                # Reutilizamos la función del protocolo
                mensaje = pr.desencriptar_y_reasamblar(largo_contenido, paquetes_recibidos)

                if "comando" in mensaje and mensaje["comando"] == "error":
                     print(f"[BACK] Error de protocolo: {mensaje['data']}")
                     continue

                print(f"[BACK] Mensaje servidor: {mensaje}")

                # 5. PROCESAMIENTO DE COMANDOS DCCASINO
                if mensaje["comando"] == "login-exitoso":
                    self.senal_respuesta_login.emit(True, "¡Login exitoso!")
                    self.senal_mostrar_principal.emit(int(mensaje["data"]["saldo"]))
                elif mensaje["comando"] == "login-fallido":
                    self.senal_respuesta_login.emit(False, mensaje["data"])
                elif mensaje["comando"] == "apuesta-aceptada":
                    self.senal_actualizar_saldo.emit(mensaje["data"]["nuevo_saldo"])
                elif mensaje["comando"] == "apuesta-fallida":
                    print(f"Apuesta fallida: {mensaje['data']}")
                elif mensaje.get("comando") == "sala-aceptada":
                    # Opcional: notificar que se entró a sala
                    pass
                # Delegar otros mensajes a juego_casino via señal
                self.senal_actualizar_juego.emit(mensaje)
                
            except Exception as e:
                print(f"[BACK] Error en la comunicación con el servidor: {e}")
                print("[CONEXIÓN] Servidor desconectado. Cerrando DCCasino.")
                break # Terminar el thread si hay un error fatal

    def enviar_mensaje(self, mensaje: dict) -> None:
        # Usar la función helper del protocolo
        paquetes_a_enviar = pr.empaquetar_mensaje(mensaje)

        # 3. Envío de todos los paquetes
        for paquete in paquetes_a_enviar:
            self.socket.sendall(paquete)