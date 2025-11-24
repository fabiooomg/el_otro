import sys
from PyQt5.QtWidgets import QApplication
# Importar las nuevas clases de ventana y la lógica de backend
from frontend.ventanas import (VentanaLogin, VentanaPrincipal,
                               VentanaBlackjack, VentanaAviator) 
from backend.juego_casino import DCCasinoBackend 


class DCCasinoApp: # Renombrar la clase principal
    def __init__(self) -> None:
        """
        Instanciamos todas las ventanas y clases necesarias
        """
        # 1. Instanciar todas las ventanas (ya no reciben host/port)
        self.frontend_login = VentanaLogin()
        self.frontend_principal = VentanaPrincipal()
        self.frontend_blackjack = VentanaBlackjack()
        self.frontend_aviator = VentanaAviator()
        
        # 2. Instanciar el backend (tampoco recibe host/port)
        self.backend = DCCasinoBackend()

    def conectar(self) -> None:
        """
        Conectamos todas las señales entre ventanas y backend para definir el flujo
        """
        # --- 1. Flujo de Autenticación (Login) ---
        
        # UI -> Backend: Acciones del usuario
        self.frontend_login.senal_intentar_login.connect(self.backend.intentar_login)
        self.frontend_login.senal_intentar_registro.connect(self.backend.intentar_registro)
        
        # Backend -> UI: Respuesta y Transición
        self.backend.senal_respuesta_login.connect(self.frontend_login.recibir_respuesta_login)
        # Éxito: Esconder login y mostrar principal
        self.backend.senal_login_exitoso.connect(self.frontend_login.hide)
        self.backend.senal_login_exitoso.connect(self.frontend_principal.mostrar_ventana)
       # --- 2. Flujo Principal (Lobby) ---

        # Backend -> UI: Actualizar Saldo 
        self.backend.senal_actualizar_saldo.connect(self.frontend_principal.actualizar_saldo)
        self.backend.senal_actualizar_saldo.connect(self.frontend_blackjack.actualizar_saldo) # Corregido el nombre del slot
        self.backend.senal_actualizar_saldo.connect(self.frontend_aviator.actualizar_saldo)   # Corregido el nombre del slot
        
        # ⚠️ CRÍTICO: Solicitud y Recepción de Historial Global
        self.frontend_principal.senal_solicitar_historial.connect(self.backend.solicitar_historial_global)
        self.backend.senal_historial_listo.connect(self.frontend_principal.mostrar_historial)

        # UI -> UI (Transición a juegos)
        self.frontend_principal.senal_entrar_blackjack.connect(self.entrar_blackjack)
        self.frontend_principal.senal_entrar_aviator.connect(self.entrar_aviator)

        # Backend -> UI: Actualización del estado del juego
        self.backend.senal_actualizar_mesa_blackjack.connect(self.frontend_blackjack.actualizar_mesa)
        self.backend.senal_mostrar_multiplicador_aviator.connect(self.frontend_aviator.actualizar_multiplicador)
        self.backend.senal_crash_aviator.connect(self.frontend_aviator.mostrar_crash)
        
        # --- 3. Flujo de Juegos (Acciones y Retorno) ---

        # UI -> Backend: Comandos de juego
        self.frontend_blackjack.senal_apostar_blackjack.connect(self.backend.apostar_blackjack)
        self.frontend_blackjack.senal_pedir_carta.connect(self.backend.pedir_carta)
        self.frontend_blackjack.senal_plantarse.connect(self.backend.plantarse_blackjack)
        
        # ⚠️ CRÍTICO: Conexiones de Aviator
        self.frontend_aviator.senal_apostar_aviator.connect(self.backend.apostar_aviator)
        self.frontend_aviator.senal_retirarse.connect(self.backend.retirarse_aviator)
        
        # UI -> UI: Retorno al menú principal
        self.frontend_blackjack.senal_volver_principal.connect(self.volver_principal)
        self.frontend_aviator.senal_volver_principal.connect(self.volver_principal)

    def entrar_blackjack(self):
        """ Oculta el menú principal, muestra la ventana de Blackjack y notifica al servidor. """
        self.frontend_principal.hide()
        self.frontend_blackjack.show()
        self.backend.entrar_juego("blackjack")

    def entrar_aviator(self):
        """ Oculta el menú principal, muestra la ventana de Aviator y notifica al servidor. """
        self.frontend_principal.hide()
        self.frontend_aviator.show()
        self.frontend_aviator.iniciar_ronda() # Resetear vista
        self.backend.entrar_juego("aviator")

    def volver_principal(self):
        """ Oculta la ventana de juego actual y regresa al menú principal. """
        # Ocultar ambas ventanas de juego por si acaso
        self.frontend_blackjack.hide()
        self.frontend_aviator.hide()
        
        # Mostrar principal y actualizar datos
        self.frontend_principal.show()
        self.backend.solicitar_historial_global() # Refrescar historial

    def iniciar(self) -> None:
        """
        Definimos qué sucede cuando empieza el juego. Muestra la ventana de login.
        """
        self.frontend_login.show()


if __name__ == "__main__":
    # La lógica de host/port ya se movió al backend/networking
    app = QApplication(sys.argv)
    juego = DCCasinoApp()
    juego.conectar()
    juego.iniciar()
    sys.exit(app.exec())