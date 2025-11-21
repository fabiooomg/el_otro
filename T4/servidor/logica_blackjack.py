import threading
import time
import random
# import requests # Para la API
import parametros as p

class PartidaBlackjack(threading.Thread):
    def __init__(self, servidor) -> None:
        super().__init__()
        self.servidor = servidor
        self.daemon = True
        self._stop_event = threading.Event()
        
        self.apuestas = {}  # {nombre_usuario: monto}
        self.manos = {}     # {nombre_usuario: lista_cartas}
        self.dealer_mano = []
        
        self.ronda_en_curso = False
        self.ronda_abierta = True
        self.cola_turnos = [] # Usuarios que esperan su turno
        
        # [cite_start]Definición de cartas para generar aleatoriamente [cite: 159]
        self.simbolos = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
        self.pintas = ['clubs', 'diamonds', 'hearts', 'spades'] 

        self.start()

    def run(self):
        while not self._stop_event.is_set():
            if self.ronda_abierta and len(self.apuestas) >= p.MAXIMO_JUGADORES_BLACKJACK:
                self.ronda_abierta = False
                self.iniciar_ronda()
            time.sleep(1)

    # --- Lógica central de Blackjack ---

    def calcular_valor_carta(self, simbolo) -> int:
        if simbolo in ['J', 'Q', 'K']:
            return 10
        elif simbolo == 'A':
            return 11
        else:
            return int(simbolo)

    def calcular_valor_mano(self, mano: list) -> int:
        """ Calcula el valor de la mano, ajustando Ases (1 u 11). """
        valor = sum(self.calcular_valor_carta(c['simbolo']) for c in mano)
        num_ases = sum(1 for c in mano if c['simbolo'] == 'A')
        
        # Ajustar Ases si se pasa de 21
        while valor > 21 and num_ases > 0:
            valor -= 10 # Cambia 11 por 1
            num_ases -= 1
        return valor

    def obtener_carta_aleatoria(self, oculta=False) -> dict:
        simbolo = random.choice(self.simbolos)
        pinta = random.choice(self.pintas)
        
        if oculta:
            # Usar un símbolo genérico para la carta oculta
            return {"simbolo": "XX", "pinta": "BACK", "oculta": True} 
        else:
            return {"simbolo": simbolo, "pinta": pinta, "oculta": False}

    def iniciar_ronda(self):
        self.ronda_en_curso = True
        self.ronda_abierta = False
        self.dealer_mano = []
        self.manos = {u: [] for u in self.apuestas.keys()}
        self.cola_turnos = list(self.apuestas.keys())
        
        # [cite_start]Repartición inicial (una pública, una privada) [cite: 150]
        for user in self.apuestas.keys():
            self.manos[user].append(self.obtener_carta_aleatoria(oculta=False)) # Pública
        
        self.dealer_mano.append(self.obtener_carta_aleatoria(oculta=False)) # Pública del Dealer

        for user in self.apuestas.keys():
            self.manos[user].append(self.obtener_carta_aleatoria(oculta=True)) # Privada del Jugador

        self.dealer_mano.append(self.obtener_carta_aleatoria(oculta=True)) # Privada del Dealer
        
        # Iniciar el primer turno
        self.iniciar_turno_jugador()
        
    def iniciar_turno_jugador(self):
        if not self.cola_turnos:
            return self.turno_dealer() # Si no hay más jugadores, pasa al dealer

        jugador_actual = self.cola_turnos[0]
        self.notificar_clientes({"comando": "turno-jugador", "usuario": jugador_actual})

    def procesar_pedir_carta(self, nombre_usuario: str):
        """ Asigna una nueva carta al jugador si es su turno. """
        carta_nueva = self.obtener_carta_aleatoria(oculta=False)
        self.manos[nombre_usuario].append(carta_nueva)
        valor = self.calcular_valor_mano(self.manos[nombre_usuario])
        
        if valor > 21:
            # [cite_start]Jugador se pasa (Bust), termina su turno inmediatamente [cite: 153]
            self.finalizar_turno_jugador(nombre_usuario, bust=True)
        else:
            # Notificar el estado actualizado de la mesa
            self.notificar_clientes_estado_mesa()

    def procesar_plantarse(self, nombre_usuario: str):
        self.finalizar_turno_jugador(nombre_usuario)

    def finalizar_turno_jugador(self, nombre_usuario: str, bust=False):
        """ Mueve el turno al siguiente jugador. """
        self.cola_turnos.pop(0) # Quita el jugador actual de la cola
        self.iniciar_turno_jugador()

    def turno_dealer(self):
        """ Lógica de la casa para pedir cartas. """
        self.ronda_en_curso = False
        
        # [cite_start]1. Revelar carta oculta (Actualizar el objeto carta oculta) [cite: 154]
        # Aquí se debe encontrar la carta oculta y reemplazarla por una nueva carta visible
        
        # [cite_start]2. Pedir carta hasta >= 17 [cite: 155-156]
        while self.calcular_valor_mano(self.dealer_mano) < 17:
            carta_nueva = self.obtener_carta_aleatoria(oculta=False)
            self.dealer_mano.append(carta_nueva)
            # Notificar cada nueva carta (con pausas si es posible)

        self.balance_de_pagos()

    def balance_de_pagos(self):
        dealer_valor = self.calcular_valor_mano(self.dealer_mano)
        resultados_ronda = []

        for user, apuesta in self.apuestas.items():
            user_valor = self.calcular_valor_mano(self.manos.get(user, []))
            ganancia = 0
            
            # [cite_start]Lógica de pagos basada en el enunciado [cite: 162-166]
            # ... implementar los 3 casos: Dealer se pasa, Dealer 17-20, Dealer 21 ...
            
            # Registrar y actualizar vía API (requests)
            # self.llamar_api_patch(user, ganancia) 
            resultados_ronda.append({"usuario": user, "monto": ganancia})

        # Registrar resultados globales de la partida vía API (POST /games/blackjack)
        # self.llamar_api_post_games("blackjack", resultados_ronda)
        
        self.reiniciar_sala()

    def notificar_clientes_estado_mesa(self):
        """ Envía el estado actual de la mesa a todos los jugadores. """
        # Lógica para enviar el estado de manos y turno
        pass
        
    def reiniciar_sala(self):
        self.apuestas.clear()
        self.ronda_abierta = True
        self.notificar_clientes({"comando": "periodo-apuestas-abierto"})