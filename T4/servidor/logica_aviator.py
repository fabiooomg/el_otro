import threading
import time
import math
import json
import random
import requests # Permitida para llamadas a la API
import parametros as p

class PartidaAviator(threading.Thread):
    def __init__(self, servidor) -> None:
        super().__init__()
        self.servidor = servidor # Referencia al Servidor principal
        self.daemon = True
        self._stop_event = threading.Event()

        self.apuestas = {}  # {nombre_usuario: monto}
        self.retirados = {} # {nombre_usuario: multiplicador_retiro}
        
        self.multiplicador_actual = 1.00
        self.t_crash = 0.0
        self.tiempo_transcurrido = 0.0
        
        self.ronda_en_curso = False
        self.ronda_abierta = True
        
        # Iniciar el ciclo de vida de la sala
        self.start() 

    def run(self):
        while not self._stop_event.is_set():
            if self.ronda_abierta:
                # 1. Esperar al periodo de apuestas
                if len(self.apuestas) >= p.MAXIMO_JUGADORES_AVIATOR:
                    self.ronda_abierta = False
                    self.iniciar_ronda()
                else:
                    time.sleep(1)
            
            elif self.ronda_en_curso:
                self.bucle_vuelo()
            
            else: # Ronda terminada, esperando reinicio
                time.sleep(p.TIEMPO_ENTRE_RONDAS) # Nuevo parámetro de tiempo de espera
                self.reiniciar_sala()

    def iniciar_ronda(self):
        self.ronda_en_curso = True
        self.tiempo_transcurrido = 0.0
        self.multiplicador_actual = 1.00
        self.retirados.clear()
        
        # [cite_start]Cálculo del tiempo de crash (random.betavariate) [cite: 118-122]
        beta_val = random.betavariate(1.4, 4.0)
        self.t_crash = beta_val * p.DURACION_RONDA_AVIATOR
        
        print(f"[AVIATOR] Ronda iniciada. Crash en: {self.t_crash:.2f}s")
        # Notificar a los clientes el inicio
        self.notificar_clientes({"comando": "ronda-aviator-iniciada"})

    def bucle_vuelo(self):
        # Usamos un paso de tiempo pequeño para simular el tiempo real
        paso_tiempo = 0.1 
        while self.tiempo_transcurrido < self.t_crash:
            time.sleep(paso_tiempo)
            self.tiempo_transcurrido += paso_tiempo
            
            # [cite_start]Cálculo del multiplicador M(t) [cite: 129-130]
            self.multiplicador_actual = 1 + (math.exp(0.55 * self.tiempo_transcurrido) - 1)

            # Sincronización: Envía el multiplicador a los clientes
            self.notificar_clientes({
                "comando": "multiplicador-update", 
                "multiplicador": float(f"{self.multiplicador_actual:.2f}")
            })
            
        # Fin de ronda: CRASH
        self.terminar_ronda()

    def registrar_apuesta(self, nombre_usuario: str, monto: int):
        if not self.ronda_en_curso and self.ronda_abierta and nombre_usuario not in self.apuestas:
            self.apuestas[nombre_usuario] = monto
            # Lógica para notificar a los clientes sobre la nueva apuesta
            self.notificar_clientes({"comando": "nueva-apuesta-aviator", "usuario": nombre_usuario, "monto": monto})

    def retirar_apuesta(self, nombre_usuario: str):
        if self.ronda_en_curso and nombre_usuario in self.apuestas and nombre_usuario not in self.retirados:
            monto_apostado = self.apuestas[nombre_usuario]
            ganancia = int(monto_apostado * self.multiplicador_actual)
            
            # Registrar retiro
            self.retirados[nombre_usuario] = self.multiplicador_actual
            
            # Actualizar saldo vía API (incluye devolución de apuesta + ganancia)
            self.llamar_api_patch(nombre_usuario, ganancia) 
            
            # Notificar
            self.notificar_clientes({
                "comando": "retiro-exitoso", 
                "usuario": nombre_usuario, 
                "ganancia": ganancia
            })
            
    def terminar_ronda(self):
        """ Gestiona el crash y el balance final. """
        self.ronda_en_curso = False
        print(f"[AVIATOR] CRASH a {self.multiplicador_actual:.2f}x")
        
        resultados_a_loguear = []
        
        for usuario, apuesta in self.apuestas.items():
            if usuario not in self.retirados:
                # Pierde el 100% (la API ya descontó la apuesta inicial, se registra la pérdida)
                perdida = -apuesta
                resultados_a_loguear.append({"usuario": usuario, "monto": perdida})

        # Registrar resultados de las pérdidas (las ganancias ya se registraron en 'retirar_apuesta')
        self.llamar_api_post_games("aviator", resultados_a_loguear)

        # Notificar el resultado del crash
        self.notificar_clientes({
            "comando": "ronda-finalizada", 
            "multiplicador_final": float(f"{self.multiplicador_actual:.2f}")
        })
        
    def reiniciar_sala(self):
        """ Limpia el estado para iniciar un nuevo periodo de apuestas. """
        self.apuestas.clear()
        self.ronda_abierta = True
        self.tiempo_transcurrido = 0.0
        self.multiplicador_actual = 1.00
        self.notificar_clientes({"comando": "periodo-apuestas-abierto"})

    def notificar_clientes(self, mensaje):
        """ Envía un mensaje a todos los ThreadCliente activos en la sala. """
        # Itera sobre los clientes que están actualmente en la sala Aviator
        for cliente_id, cliente_thread in self.servidor.clientes.items():
            if cliente_thread.juego_actual == "aviator":
                cliente_thread.mensajes_a_enviar.put(mensaje)

    # --- Métodos de Interacción con la API (requests) ---
    def llamar_api_patch(self, usuario, cambio_saldo):
        """ Llama al endpoint PATCH /users/:id para actualizar el saldo. """
        try:
            url = f"http://{self.servidor.HOST}:{self.servidor.API_PORT}/users/{usuario}"
            headers = {'Authorization': p.TOKEN_AUTENTICACION, 'Content-Type': 'application/json'}
            payload = {'cambio_saldo': cambio_saldo}
            
            response = requests.patch(url, headers=headers, json=payload)
            # Manejar la respuesta...
            return response.status_code == 200
        except Exception as e:
            print(f"[API ERROR] Fallo al actualizar saldo de {usuario}: {e}")
            return False

    def llamar_api_post_games(self, juego, resultados):
        """ Llama al endpoint POST /games/:juego para registrar resultados. """
        try:
            url = f"http://{self.servidor.HOST}:{self.servidor.API_PORT}/games/{juego}"
            headers = {'Authorization': p.TOKEN_AUTENTICACION, 'Content-Type': 'application/json'}

            response = requests.post(url, headers=headers, json=resultados)
            return response.status_code == 200
        except Exception as e:
            print(f"[API ERROR] Fallo al postear resultados: {e}")
            return False