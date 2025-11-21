from PyQt5.QtCore import QObject, pyqtSignal
from backend.networking import Cliente
import parametros as p 

class DCCasinoBackend(QObject):
    # Señales para notificar al Front-end (UI)
    senal_login_exitoso = pyqtSignal(str, int) # Usuario, Saldo
    senal_respuesta_login = pyqtSignal(bool, str) # Éxito/Fallo, Mensaje
    senal_actualizar_saldo = pyqtSignal(int)
    # ... más señales de juego: senal_actualizar_mesa_blackjack, senal_mostrar_multiplicador_aviator

    def __init__(self) -> None:
        super().__init__()
        
        self.nombre_usuario = ""
        self.saldo_local = p.SALDO_INICIAL # Mantener un registro local
        
        self.cliente = Cliente() # Ya no necesita argumentos
        
        # Conectar las señales del Networking con los métodos de procesamiento
        self.cliente.senal_respuesta_login.connect(self.procesar_login)
        self.cliente.senal_actualizar_saldo.connect(self.actualizar_saldo)
        self.cliente.senal_actualizar_juego.connect(self.procesar_actualizacion_juego)
        # ... otras conexiones de red (ej. desconexión repentina) ...


    def intentar_login(self, usuario: str, clave: str) -> None:
        """ Traduce el intento de login de la UI a un mensaje de red. """
        print(f"[BACKEND] Intento de login para {usuario}")
        mensaje = {
            "comando": "login",
            "data": {"usuario": usuario, "clave": clave}
        }
        self.cliente.enviar_mensaje(mensaje)

    def intentar_registro(self, usuario: str, clave: str) -> None:
        """ Traduce el intento de registro de la UI a un mensaje de red. """
        print(f"[BACKEND] Intento de registro para {usuario}")
        mensaje = {
            "comando": "registro",
            "data": {"usuario": usuario, "clave": clave}
        }
        self.cliente.enviar_mensaje(mensaje)
        
    def procesar_login(self, exito: bool, mensaje: str, saldo: int=0) -> None:
        """ Procesa la respuesta de login/registro del servidor. """
        self.senal_respuesta_login.emit(exito, mensaje)
        
        if exito:
            # Asumimos que el mensaje incluye el nombre y el saldo.
            self.nombre_usuario = mensaje.split(':')[0] # Esto debe ser refinado en el protocolo
            self.saldo_local = saldo
            self.senal_login_exitoso.emit(self.nombre_usuario, self.saldo_local)

    def actualizar_saldo(self, nuevo_saldo: int) -> None:
        """ Actualiza el saldo local y notifica a todas las ventanas. """
        self.saldo_local = nuevo_saldo
        self.senal_actualizar_saldo.emit(nuevo_saldo)
        
    def procesar_actualizacion_juego(self, datos_juego: dict) -> None:
        """ Distribuye los datos de juego (Aviator, Blackjack) a la ventana correcta. """
        comando = datos_juego.get("tipo_juego")
        
        if comando == "AVIATOR_UPDATE":
            # self.senal_mostrar_multiplicador_aviator.emit(datos_juego)
            pass
        elif comando == "BLACKJACK_MESA":
            # self.senal_actualizar_mesa_blackjack.emit(datos_juego)
            pass
        # ... etc.

    # D. Métodos de Acción del Juego (UI -> Red)
    
    def apostar_blackjack(self, monto: int) -> None:
        if monto > 0 and monto <= self.saldo_local:
            mensaje = {"comando": "apostar", "juego": "blackjack", "monto": monto}
            self.cliente.enviar_mensaje(mensaje)
        else:
            # Notificar a la UI de un error de saldo insuficiente
            pass
            
    # [Resto de los métodos como pedir_carta, plantarse, retirarse_aviator, etc., siguen la misma estructura]