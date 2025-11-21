import socket
import json
from PyQt5.QtCore import QThread, pyqtSignal
from math import ceil
import parametros as para

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
                contenido_reasamblado = bytearray()
                paquetes_recibidos = {}

                # 2. RECIBIR PAQUETES (128 bytes cada uno)
                for _ in range(num_paquetes):
                    paquete_encriptado = self.recibir_bytes(para.CHUNK_SIZE + 4) # 128 bytes
                    
                    # Desencriptar
                    paquete = self.cifrar_xor(paquete_encriptado)

                    # Obtener Índice (4 bytes BIG ENDIAN)
                    indice = int.from_bytes(paquete[:4], "big")
                    
                    # Obtener Contenido (124 bytes)
                    chunk = paquete[4:]
                    
                    paquetes_recibidos[indice] = chunk

                # 3. REASAMBLAR CONTENIDO EN ORDEN Y DECODIFICAR
                for indice in sorted(paquetes_recibidos.keys()):
                    contenido_reasamblado.extend(paquetes_recibidos[indice])
                
                # Recortar el relleno (padding)
                bytes_mensaje = bytes(contenido_reasamblado[:largo_contenido])

                # 4. JSON LOAD
                mensaje = json.loads(bytes_mensaje.decode("utf-8"))
                print(f"[BACK] Mensaje servidor: {mensaje}")

                # 5. PROCESAMIENTO DE COMANDOS DCCASINO
                if mensaje["comando"] == "login-exitoso":
                    self.senal_respuesta_login.emit(True, "¡Login exitoso!")
                    self.senal_mostrar_principal.emit()
                elif mensaje["comando"] == "saldo-actualizado":
                    self.senal_actualizar_saldo.emit(mensaje["data"]["saldo"])
                # ... y así con todos los comandos de juego
                
            except Exception as e:
                print(f"[BACK] Error en la comunicación con el servidor: {e}")
                print("[CONEXIÓN] Servidor desconectado. Cerrando DCCasino.")
                break # Terminar el thread si hay un error fatal

    def enviar_mensaje(self, mensaje: dict) -> None:
        bytes_contenido = json.dumps(mensaje).encode("utf-8")
        largo_contenido = len(bytes_contenido)

        # Enviar el largo total del contenido (LITTLE ENDIAN)
        self.socket.sendall(largo_contenido.to_bytes(4, "little"))
        paquetes_a_enviar = []

        # 2. Fragmentación y Encriptación
        for i in range(0, largo_contenido, para.CHUNK_SIZE):
            # 2.1 Obtener el chunk (124 bytes)
            chunk = bytes_contenido[i:i + para.CHUNK_SIZE]

            # 2.2 Relleno (Padding) con bytes nulos si el chunk es el último y es más corto
            if len(chunk) < para.CHUNK_SIZE:
                chunk += b'\x00' * (para.CHUNK_SIZE - len(chunk))

            # 2.3 Enumeración del paquete (4 bytes BIG ENDIAN)
            indice_bytes = i.to_bytes(4, "big") # El índice es la posición de inicio

            # Paquete de 128 bytes antes de encriptar
            paquete = indice_bytes + chunk 

            # 2.4 Encriptación XOR (Función auxiliar)
            paquete_encriptado = self.cifrar_xor(paquete)

            paquetes_a_enviar.append(paquete_encriptado)

        # 3. Envío de todos los paquetes
        for paquete in paquetes_a_enviar:
            self.socket.sendall(paquete)
            
    # Mantenla dentro de la clase Cliente o como una función de modulo:

    def cifrar_xor(self, paquete: bytes) -> bytes:
        cifrado = b''
        for i, byte in enumerate(paquete):
            # Aplica XOR con el byte correspondiente de la clave de 128 bytes
            cifrado += bytes([byte ^ para.CLAVE_CASINO[i % len(para.CLAVE_CASINO)]])
        return cifrado