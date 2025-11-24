from PyQt5.QtCore import QObject, pyqtSignal
from backend.networking import Cliente
import parametros as p 

class DCCasinoBackend(QObject):
    # Señales para notificar al Front-end (UI)
    senal_login_exitoso = pyqtSignal(str, int) # Usuario, Saldo
    senal_respuesta_login = pyqtSignal(bool, str) # Éxito/Fallo, Mensaje
    senal_actualizar_saldo = pyqtSignal(int)
    senal_historial_listo = pyqtSignal(list)

    # Señales de juego
    senal_actualizar_mesa_blackjack = pyqtSignal(dict)
    senal_mostrar_multiplicador_aviator = pyqtSignal(float)
    senal_crash_aviator = pyqtSignal(float)

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
        comando = datos_juego.get("comando")
        data = datos_juego.get("data")
        
        if comando == "estado-mesa": # Blackjack
            self.senal_actualizar_mesa_blackjack.emit(data)

        elif comando == "multiplicador-update": # Aviator
            multiplicador = float(data.get("multiplicador", 1.0))
            self.senal_mostrar_multiplicador_aviator.emit(multiplicador)

        elif comando == "ronda-finalizada": # Aviator Crash
            multiplicador_final = float(data.get("multiplicador_final", 1.0))
            self.senal_crash_aviator.emit(multiplicador_final)

        elif comando == "historial-global":
             # Recibe el historial del servidor y lo pasa al frontend
             historial = data if isinstance(data, list) else []
             self.senal_historial_listo.emit(historial)

    # D. Métodos de Acción del Juego (UI -> Red)
    
    def entrar_juego(self, juego: str) -> None:
        """ Notifica al servidor que el usuario entra a una sala. """
        self.cliente.enviar_mensaje({"comando": "entrar-juego", "data": {"juego": juego}})

    def solicitar_historial_global(self) -> None:
        """ Solicita el historial de ganancias al servidor. """
        self.cliente.enviar_mensaje({"comando": "solicitar-historial"})

    def apostar_blackjack(self, monto: int) -> None:
        if monto > 0 and monto <= self.saldo_local:
            mensaje = {"comando": "apostar", "juego": "blackjack", "monto": monto}
            self.cliente.enviar_mensaje(mensaje)
        else:
            # Podríamos emitir señal de error, pero por ahora solo log
            print("[BACKEND] Saldo insuficiente para apostar.")

    def pedir_carta(self) -> None:
        self.cliente.enviar_mensaje({"comando": "pedir-carta"})

    def plantarse_blackjack(self) -> None:
        self.cliente.enviar_mensaje({"comando": "plantarse"})

    def apostar_aviator(self, monto: int) -> None:
        if monto > 0 and monto <= self.saldo_local:
            mensaje = {"comando": "apostar", "juego": "aviator", "monto": monto}
            self.cliente.enviar_mensaje(mensaje)
        else:
             print("[BACKEND] Saldo insuficiente para apostar.")

    def retirarse_aviator(self) -> None:
        self.cliente.enviar_mensaje({"comando": "retirarse"})