import threading
import json
import socket
from queue import Queue
from math import ceil
import time
import os
import http.client # Necesario para las llamadas a la API
import parametros as p
import protocolo as pr 

class ThreadCliente(threading.Thread):
    
    def __init__(self, id_cliente: int, socket_cliente: socket, address: tuple, servidor_central) -> None:
        super().__init__()
        
        self.id_cliente = id_cliente
        self.socket = socket_cliente
        self.address = address
        self.servidor_central = servidor_central
        self.daemon = True
        
        # Atributos de Sesión y Juego
        self.nombre_usuario = None 
        self.saldo_actual = p.SALDO_INICIAL
        self.juego_actual = None # Ej: "aviator", "blackjack"
        
        # Mecanismo de Concurrencia para envío
        self.mensajes_a_enviar = Queue() 
        self.enviar_mensajes_thread = threading.Thread(
            target=self.procesar_mensajes_a_enviar, daemon=True
        )
        
        # ⚠️ CRÍTICO 1: Inicializar la conexión con la API
        # Necesitamos saber dónde está la API para usar http.client
        RUTA_CONEXION = os.path.join("servidor", "conexion.json")
        try:
            with open(RUTA_CONEXION, 'r') as file:
                datos_conexion = json.load(file)
                # Almacenar HOST y PORT de la API
                self.HOST_API = datos_conexion.get("host") 
                self.PORT_API = datos_conexion.get("puertoAPI")
        except FileNotFoundError:
             print("[ERROR] Archivo conexion.json no encontrado.")

    def run(self) -> None:
        """ Método principal del thread: inicia envío y escucha. """
        self.enviar_mensajes_thread.start()
        self.listen()
        
    # --- Métodos de Red (Envío y Recepción) ---

    def recibir_bytes(self, cantidad: int) -> bytearray:
        """
        Recibe N cantidad de bytes.
        """
        bytes_leidos = bytearray()
        buffer_size = 4096
        while len(bytes_leidos) < cantidad:
            cantidad_restante = cantidad - len(bytes_leidos)
            bytes_leer = min(buffer_size, cantidad_restante)
            try:
                respuesta = self.socket.recv(bytes_leer)
                if not respuesta:
                    return None
                bytes_leidos += respuesta
            except OSError:
                return None
        return bytes_leidos

    def listen(self) -> None:
        """
        Ciclo principal de escucha de mensajes del cliente.
        """
        while True:
            try:
                # 1. Recibir Largo (4 bytes LITTLE ENDIAN)
                largo_bytes = self.recibir_bytes(4)
                if not largo_bytes:
                    print(f"Cliente {self.id_cliente} desconectado.")
                    break
                largo_contenido = int.from_bytes(largo_bytes, "little")

                # 2. Recibir Paquetes
                num_paquetes = ceil(largo_contenido / p.CHUNK_SIZE)
                paquetes_recibidos = {}

                for _ in range(num_paquetes):
                    # 128 bytes por paquete (4 idx + 124 contenido)
                    paquete_encriptado = self.recibir_bytes(p.CHUNK_SIZE + 4)
                    if not paquete_encriptado:
                        raise ConnectionResetError

                    # Desencriptar
                    paquete = pr.cifrar_xor(paquete_encriptado)

                    # Separar Índice y Chunk
                    indice = int.from_bytes(paquete[:4], "big")
                    chunk = paquete[4:]
                    paquetes_recibidos[indice] = chunk

                # 3. Reensamblar y procesar
                mensaje = pr.desencriptar_y_reasamblar(largo_contenido, paquetes_recibidos)
                # Si ocurrió error de JSON, retorna dict con error, pero no rompe el loop

                print(f"[SRV] Mensaje de cliente {self.id_cliente}: {mensaje}")
                self.procesar_mensaje(mensaje)

            except (ConnectionResetError, ConnectionAbortedError):
                print(f"Error conexión cliente {self.id_cliente}")
                break
            except Exception as e:
                print(f"Error inesperado en ThreadCliente {self.id_cliente}: {e}")
                break

        self.socket.close()

    def procesar_mensajes_a_enviar(self) -> None:
        """
        Toma mensajes de la cola y los envía encriptados.
        """
        while True:
            try:
                mensaje = self.mensajes_a_enviar.get()
                if mensaje is None:
                    break

                # Usar protocolo para obtener lista de paquetes
                paquetes = pr.empaquetar_mensaje(mensaje)

                # El primer elemento de la lista es el prefijo de largo
                # Los siguientes son los paquetes encriptados
                for pkt in paquetes:
                    self.socket.sendall(pkt)
            except OSError:
                print("Error enviando mensaje, socket cerrado.")
                break
            except Exception as e:
                print(f"Error en envío: {e}")
    
    # --- CRÍTICO 2: Helper de Llamada API ---
    def realizar_llamada_api(self, method: str, path: str, body: dict = None) -> tuple:
        """ 
        Función helper para realizar llamadas a la API de Flask.
        Retorna (status_code, response_data).
        """
        conn = http.client.HTTPConnection(self.HOST_API, self.PORT_API)
        headers = {
            'Authorization': p.TOKEN_AUTENTICACION,
            'Content-Type': 'application/json'
        }
        
        try:
            body_json = json.dumps(body) if body else None
            conn.request(method, path, body_json, headers)
            response = conn.getresponse()
            
            data = response.read().decode()
            response_data = json.loads(data) if data else {}
            
            return response.status, response_data
        
        except Exception as e:
            print(f"[API ERROR] Fallo en {method} {path}: {e}")
            return 500, {"error": "Fallo en la comunicación con la API."}
        finally:
            conn.close()

    # --- Lógica de Procesamiento de Mensajes (CRÍTICO 3) ---
    def procesar_mensaje(self, mensaje: dict) -> None:
        """
        Analiza el mensaje recibido del cliente y llama a la lógica correspondiente.
        """
        comando = mensaje.get("comando")
        data = mensaje.get("data", {})
        
        # --- 1. AUTENTICACIÓN ---
        if comando == "login":
            usuario = data.get("usuario")
            clave = data.get("clave")
            
            # 1. Llamar a la API para verificar credenciales y obtener saldo
            status, res_data = self.realizar_llamada_api("GET", f"/users/{usuario}", {"clave": clave})
            
            if status == 200:
                self.nombre_usuario = usuario 
                self.saldo_actual = res_data.get("saldo", 0) 
                respuesta = {
                    "comando": "login-exitoso", 
                    "data": {"usuario": self.nombre_usuario, "saldo": self.saldo_actual}
                }
            else:
                respuesta = {"comando": "login-fallido", "data": res_data.get("error", "Error desconocido.")}
            
            self.mensajes_a_enviar.put(respuesta)

        # --- 2. ENTRAR A JUEGO ---
        elif comando == "entrar-juego":
            juego = data["juego"] # Ej: "aviator" o "blackjack"
            sala = self.servidor_central.salas.get(juego)
            
            # ⚠️ CRÍTICO 3.1: Delegar la verificación de entrada a la lógica de juego
            if sala and sala.puede_entrar(self.nombre_usuario):
                self.juego_actual = juego
                sala.agregar_jugador(self) # Registrar el thread en la sala
                respuesta = {"comando": "sala-aceptada", "data": juego}
            else:
                respuesta = {"comando": "sala-rechazada", "data": "Mesa llena o ronda en curso."}
            
            self.mensajes_a_enviar.put(respuesta)
        
        # --- 3. ACCIONES DE JUEGO GENERALES ---
        elif comando == "apostar":
            monto = data.get("monto", 0)
            juego = self.juego_actual
            
            if monto <= 0 or monto > self.saldo_actual:
                respuesta = {"comando": "apuesta-fallida", "data": "Saldo insuficiente."}
                self.mensajes_a_enviar.put(respuesta)
                return

            # 1. Descontar saldo vía API (PATCH /users/:id)
            status, res_data = self.realizar_llamada_api(
                "PATCH", 
                f"/users/{self.nombre_usuario}", 
                {"cambio_saldo": -monto} # Descuento
            )

            if status == 200:
                self.saldo_actual = res_data.get("nuevo_saldo", self.saldo_actual - monto) 
                
                # ⚠️ CRÍTICO 3.2: Notificar a la sala de juego
                self.servidor_central.salas[juego].registrar_apuesta(self.nombre_usuario, monto)
                
                respuesta = {"comando": "apuesta-aceptada", "data": {"nuevo_saldo": self.saldo_actual}}
            else:
                respuesta = {"comando": "apuesta-fallida", "data": res_data.get("error", "Error API al descontar.")}
            
            self.mensajes_a_enviar.put(respuesta)

        # --- 4. ACCIONES DE JUEGO ESPECÍFICAS ---
        elif comando == "retirarse":
            # ⚠️ CRÍTICO 3.3: Llamar al método de retiro en la sala Aviator
            if self.juego_actual == "aviator":
                self.servidor_central.salas["aviator"].retirar_apuesta(self.nombre_usuario)
            # La respuesta de ganancia o éxito la envía la propia lógica de Aviator al cliente

        elif comando == "pedir-carta":
            # ⚠️ CRÍTICO 3.4: Llamar al método de acción en la sala Blackjack
            if self.juego_actual == "blackjack":
                self.servidor_central.salas["blackjack"].procesar_pedir_carta(self.nombre_usuario)
                
        elif comando == "plantarse":
            if self.juego_actual == "blackjack":
                self.servidor_central.salas["blackjack"].procesar_plantarse(self.nombre_usuario)

        elif comando == "solicitar-historial":
            # Llamar a la API para obtener el historial global
            status, res_data = self.realizar_llamada_api("GET", "/games/historial")
            if status == 200:
                historial = res_data.get("historial", [])
                respuesta = {"comando": "historial-global", "data": historial}
            else:
                respuesta = {"comando": "error", "data": "No se pudo obtener el historial."}

            self.mensajes_a_enviar.put(respuesta)