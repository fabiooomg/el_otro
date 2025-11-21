from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QLineEdit, 
                             QComboBox, QTableWidget, QHBoxLayout, QVBoxLayout, QGridLayout, QFrame,
                             QMessageBox, QHeaderView, QTableWidgetItem) # Añadido QHeaderView, QTableWidgetItem
from PyQt5.QtCore import Qt, pyqtSignal, QTimer 
from PyQt5.QtGui import QFont, QPixmap, QColor # Añadido QColor para el historial
import parametros as p
import os # Necesario para la función de cargar cartas (aunque no está aquí, es buena práctica)

# NOTA: Se eliminan las importaciones de PyQt5.QtMultimedia no utilizadas.

## 1. VENTANALOGIN
class VentanaLogin(QWidget):
    senal_intentar_login = pyqtSignal(str, str)
    senal_intentar_registro = pyqtSignal(str, str)

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("DCCasino: Ingreso")
        self.setGeometry(200, 200, 400, 250)
        
        # Widgets
        self.titulo = QLabel("DCCasino", self)
        self.titulo.setFont(QFont("Arial", 24))
        
        self.label_usuario = QLabel("Usuario:", self)
        self.input_usuario = QLineEdit(self)
        
        self.label_clave = QLabel("Clave:", self)
        self.input_clave = QLineEdit(self)
        self.input_clave.setEchoMode(QLineEdit.Password)
        
        self.boton_login = QPushButton("Iniciar Sesión", self)
        self.boton_registro = QPushButton("Registrar", self)
        
        self.mensaje_estado = QLabel("Esperando conexión...", self)
        
        # Layouts
        v_layout = QVBoxLayout()
        h_buttons = QHBoxLayout()
        
        h_buttons.addWidget(self.boton_login)
        h_buttons.addWidget(self.boton_registro)
        
        v_layout.addWidget(self.titulo, alignment=Qt.AlignCenter)
        v_layout.addWidget(self.label_usuario)
        v_layout.addWidget(self.input_usuario)
        v_layout.addWidget(self.label_clave)
        v_layout.addWidget(self.input_clave)
        v_layout.addLayout(h_buttons)
        v_layout.addWidget(self.mensaje_estado)

        self.setLayout(v_layout)

        # Conexiones
        self.boton_login.clicked.connect(self.enviar_login)
        self.boton_registro.clicked.connect(self.enviar_registro)
        
    def enviar_login(self) -> None:
        user = self.input_usuario.text()
        clave = self.input_clave.text()
        self.senal_intentar_login.emit(user, clave)

    def enviar_registro(self) -> None:
        user = self.input_usuario.text()
        clave = self.input_clave.text()
        self.senal_intentar_registro.emit(user, clave)

    def recibir_respuesta_login(self, exito: bool, mensaje: str) -> None:
        if exito:
            self.hide()
        else:
            QMessageBox.warning(self, "Error de Ingreso", mensaje)
            self.mensaje_estado.setText(mensaje)
            self.mensaje_estado.setStyleSheet("color: red")
            
    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            self.enviar_login()


## 2. VENTANAPRINCIPAL
class VentanaPrincipal(QWidget):
    senal_entrar_blackjack = pyqtSignal()
    senal_entrar_aviator = pyqtSignal()
    senal_entrar_ruleta = pyqtSignal() 
    senal_cargar_dinero = pyqtSignal(int)
    senal_solicitar_historial = pyqtSignal() # 💡 CRÍTICO: Señal para pedir datos al backend
    
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("DCCasino: Menú Principal")
        self.setGeometry(100, 100, 800, 600)
        
        # Inicialización de widgets
        self.nombre_usuario = QLabel("Jugador: ", self)
        self.saldo_actual = QLabel("Saldo: $0", self) # E
        
        # F: Historial (QTableWidget)
        self.ultimas_ganancias = QTableWidget(self) 
        self.ultimas_ganancias.setColumnCount(3)
        self.ultimas_ganancias.setHorizontalHeaderLabels(["Juego", "Usuario", "Monto"])
        self.ultimas_ganancias.setRowCount(p.ULTIMAS_GANANCIAS_PRINCIPAL) 
        # Bloquear edición y asegurar que ocupe todo el espacio
        self.ultimas_ganancias.setEditTriggers(QTableWidget.NoEditTriggers)
        self.ultimas_ganancias.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # Botones de Juego (A, B, C)
        self.boton_blackjack = QPushButton("Blackjack", self)
        self.boton_aviator = QPushButton("Aviator", self)
        self.boton_ruleta = QPushButton("Ruleta (Bonus)", self)
        
        # Botón Cargar Dinero (D)
        self.boton_cargar = QPushButton("Cargar Dinero", self)
        
        # Layouts
        main_layout = QHBoxLayout()
        v_layout_juegos = QVBoxLayout()
        v_layout_historial = QVBoxLayout()
        h_layout_status = QHBoxLayout()
        
        h_layout_status.addWidget(self.nombre_usuario)
        h_layout_status.addWidget(self.saldo_actual)
        
        v_layout_historial.addWidget(self.ultimas_ganancias)
        v_layout_historial.addWidget(self.boton_cargar, alignment=Qt.AlignLeft) 

        v_layout_juegos.addWidget(self.boton_blackjack)
        v_layout_juegos.addWidget(self.boton_aviator)
        v_layout_juegos.addWidget(self.boton_ruleta)
        v_layout_juegos.addStretch(1)
        
        main_layout.addLayout(v_layout_historial, 1)
        main_layout.addLayout(v_layout_juegos, 2)
        
        full_layout = QVBoxLayout()
        full_layout.addLayout(h_layout_status)
        full_layout.addLayout(main_layout)
        self.setLayout(full_layout)
        
        # Conexiones:
        self.boton_blackjack.clicked.connect(lambda: self.senal_entrar_blackjack.emit())
        self.boton_aviator.clicked.connect(lambda: self.senal_entrar_aviator.emit())
        self.boton_ruleta.clicked.connect(lambda: self.senal_entrar_ruleta.emit())
        
    # Slots
    def mostrar_ventana(self, usuario: str, saldo: int) -> None:
        """ Muestra la ventana principal y solicita la carga del historial. """
        self.nombre_usuario.setText(f"Jugador: {usuario}")
        self.actualizar_saldo(saldo)
        self.senal_solicitar_historial.emit() # 💡 CRÍTICO: Solicita los datos de la tabla
        self.show()

    def actualizar_saldo(self, saldo: int) -> None:
        self.saldo_actual.setText(f"Saldo: ${saldo}")
        
    def mostrar_historial(self, datos: list) -> None:
        """ Slot que recibe los datos de historial del backend y popula la tabla F. """
        self.ultimas_ganancias.setRowCount(len(datos))

        for fila, registro in enumerate(datos):
            juego = registro.get("juego", "N/A")
            usuario = registro.get("usuario", "N/A")
            monto = registro.get("monto", 0)

            self.ultimas_ganancias.setItem(fila, 0, QTableWidgetItem(juego))
            self.ultimas_ganancias.setItem(fila, 1, QTableWidgetItem(usuario))
            
            item_monto = QTableWidgetItem(f"${monto}")
            # Color condicional
            if monto < 0:
                item_monto.setForeground(QColor("red"))
            else:
                item_monto.setForeground(QColor("green"))

            self.ultimas_ganancias.setItem(fila, 2, item_monto)


## 3. VENTANABLACKJACK
class VentanaBlackjack(QWidget):
    senal_apostar_blackjack = pyqtSignal(int) 
    senal_pedir_carta = pyqtSignal()
    senal_plantarse = pyqtSignal()
    senal_volver_principal = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("DCCasino: Blackjack")
        self.setStyleSheet("background-color: green;") 
        
        # Inicialización de QLabel para mostrar saldo
        self.label_saldo = QLabel("Saldo: $0", self) # Necesario para actualizar el saldo
        
        # ... (Resto de la inicialización y layouts) ...
        self.mesa_layout = QGridLayout()
        self.cartas_dealer = []
        self.cartas_jugador = []

        self.control_frame = QFrame(self) 
        self.control_frame.setStyleSheet("background-color: darkgray;")
        self.control_layout = QHBoxLayout(self.control_frame)

        self.input_apuesta = QLineEdit(self)
        self.boton_apostar = QPushButton("Apostar", self)
        self.boton_pedir = QPushButton("Pedir Carta", self)
        self.boton_plantarse = QPushButton("Plantarse", self)
        self.boton_volver = QPushButton("Volver a V. Principal", self)
        
        self.control_layout.addWidget(self.label_saldo) # Mostrar el saldo
        self.control_layout.addWidget(self.input_apuesta)
        self.control_layout.addWidget(self.boton_apostar)
        self.control_layout.addWidget(self.boton_pedir)
        self.control_layout.addWidget(self.boton_plantarse)
        self.control_layout.addWidget(self.boton_volver)
        
        main_layout = QVBoxLayout()
        main_layout.addLayout(self.mesa_layout, 3)
        main_layout.addWidget(self.control_frame, 1)
        self.setLayout(main_layout)
        
        # Conexiones
        self.boton_apostar.clicked.connect(self._emitir_apuesta)
        self.boton_pedir.clicked.connect(lambda: self.senal_pedir_carta.emit())
        self.boton_plantarse.clicked.connect(lambda: self.senal_plantarse.emit())
        self.boton_volver.clicked.connect(lambda: self.senal_volver_principal.emit())
        
    def _emitir_apuesta(self) -> None:
        try:
            monto = int(self.input_apuesta.text())
            self.senal_apostar_blackjack.emit(monto)
        except ValueError:
            QMessageBox.warning(self, "Error", "Monto de apuesta inválido.")
            
    # 💡 CRÍTICO: Slot para actualizar el saldo
    def actualizar_saldo(self, saldo: int) -> None:
        self.label_saldo.setText(f"Saldo: ${saldo}")

    def actualizar_mesa(self, datos_mesa: dict) -> None:
        pass


## 4. VENTANAAVIATOR
class VentanaAviator(QWidget):
    senal_apostar_aviator = pyqtSignal(int)
    senal_retirarse = pyqtSignal()
    senal_volver_principal = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("DCCasino: Aviator")
        
        self.ronda_activa = False
        
        # --- 1. Área de Jugadores (A) ---
        self.tabla_jugadores = QTableWidget(self)
        self.tabla_jugadores.setColumnCount(4)
        self.tabla_jugadores.setHorizontalHeaderLabels(["Jugador", "Apuesta", "Retiro", "Ganancia"])
        
        self.label_estado_ronda = QLabel("Periodo de Apuestas", self)
        self.label_temporizador = QLabel("Tiempo: 00:00", self)
        self.boton_volver = QPushButton("Volver a la ventana principal", self)
        
        v_layout_A = QVBoxLayout()
        v_layout_A.addWidget(self.tabla_jugadores)
        v_layout_A.addWidget(self.label_estado_ronda)
        v_layout_A.addWidget(self.label_temporizador)
        v_layout_A.addWidget(self.boton_volver)
        
        # --- 2. Área de Juego (B) ---
        self.area_juego = QWidget(self)
        self.area_juego.setStyleSheet("background-color: lightgray;")
        self.label_multiplicador = QLabel("1.00×", self.area_juego)
        self.label_multiplicador.setFont(QFont("Arial", 48))
        self.label_multiplicador.move(50, 50) 
        
        v_layout_B = QVBoxLayout()
        v_layout_B.addWidget(self.area_juego)

        # --- 3. Área de Apuestas (C) ---
        self.label_saldo = QLabel("Saldo: $0", self)
        self.input_monto = QLineEdit(self)
        self.boton_accion = QPushButton("Apostar ($0)", self)
        
        h_layout_C = QHBoxLayout()
        h_layout_C.addWidget(self.label_saldo)
        h_layout_C.addWidget(QLabel("Monto:"))
        h_layout_C.addWidget(self.input_monto)
        h_layout_C.addWidget(self.boton_accion)
        
        # Layout Principal
        h_central = QHBoxLayout()
        h_central.addLayout(v_layout_A, 1)
        
        v_derecha = QVBoxLayout()
        v_derecha.addLayout(v_layout_B, 2)
        v_derecha.addLayout(h_layout_C, 1)
        h_central.addLayout(v_derecha, 3)
        
        self.setLayout(h_central)

        # Conexiones
        self.boton_volver.clicked.connect(lambda: self.senal_volver_principal.emit())
        self.boton_accion.clicked.connect(self._emitir_accion)

    def _emitir_accion(self) -> None:
        if not self.ronda_activa:
            try:
                monto = int(self.input_monto.text())
                self.senal_apostar_aviator.emit(monto)
            except ValueError:
                QMessageBox.warning(self, "Error", "Monto inválido.")
        else:
            self.senal_retirarse.emit()
            
    # 💡 CRÍTICO: Slot para actualizar el saldo
    def actualizar_saldo(self, saldo: int) -> None:
        self.label_saldo.setText(f"Saldo: ${saldo}")

    def actualizar_multiplicador(self, multiplicador: float) -> None:
        self.label_multiplicador.setText(f"{multiplicador:.2f}×")
        # Aquí se debe llamar a self.area_juego.update() para redibujar la curva.
        
    def iniciar_ronda(self) -> None:
        self.ronda_activa = True
        self.boton_accion.setText("Retirar ($0)")
        self.label_estado_ronda.setText("Ronda en Curso")

    def mostrar_crash(self, multiplicador_final: float) -> None:
        self.ronda_activa = False
        self.label_multiplicador.setText(f"¡CRASH! {multiplicador_final:.2f}×")
        self.label_estado_ronda.setText("Fin de Ronda")