from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QLineEdit, 
                             QComboBox, QTableWidget, QHBoxLayout, QVBoxLayout, QGridLayout, QFrame,
                             QMessageBox, QHeaderView, QTableWidgetItem)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QRectF
from PyQt5.QtGui import QFont, QPixmap, QColor, QPainter, QPen
import math
import parametros as p
import os

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
        """
        Recibe la información de la mesa (cartas del dealer y del usuario)
        y actualiza la interfaz gráfica.
        """
        # Limpiar mesa anterior (eliminar widgets del layout)
        # Nota: QGridLayout no tiene un método clear() directo que borre widgets.
        # Hay que iterar y eliminarlos.
        while self.mesa_layout.count():
            item = self.mesa_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        # Re-dibujar cartas del Dealer
        mano_dealer = datos_mesa.get("dealer_mano", [])
        self.mesa_layout.addWidget(QLabel("Dealer:", self), 0, 0)
        for i, carta in enumerate(mano_dealer):
            lbl_carta = QLabel(self)
            pixmap = self.cargar_pixmap_carta(carta)
            if pixmap:
                lbl_carta.setPixmap(pixmap.scaled(80, 120, Qt.KeepAspectRatio))
            self.mesa_layout.addWidget(lbl_carta, 0, i + 1)

        # Re-dibujar cartas del Jugador
        mano_jugador = datos_mesa.get("mano_jugador", [])
        self.mesa_layout.addWidget(QLabel("Tú:", self), 1, 0)
        for i, carta in enumerate(mano_jugador):
            lbl_carta = QLabel(self)
            pixmap = self.cargar_pixmap_carta(carta)
            if pixmap:
                lbl_carta.setPixmap(pixmap.scaled(80, 120, Qt.KeepAspectRatio))
            self.mesa_layout.addWidget(lbl_carta, 1, i + 1)

    def cargar_pixmap_carta(self, carta_dict: dict) -> QPixmap:
        """
        Carga la imagen de la carta basada en el diccionario {'simbolo': 'A', 'pinta': 'hearts'}
        o {'oculta': True}.
        """
        if carta_dict.get("oculta"):
            path = p.RUTA_CARTA_BOCA_ABAJO
        else:
            simbolo = carta_dict.get("simbolo")
            pinta = carta_dict.get("pinta")
            # Formato de nombre: card_hearts_A.png, card_clubs_10.png
            # Asegurarse de que el path sea correcto.
            # En Assets/Blackjack los nombres son tipo: card_hearts_05.png, card_clubs_A.png
            # Necesitamos mapear simbolos si es necesario.
            # Según list_files: card_hearts_02.png ... card_hearts_10.png, card_hearts_A.png, card_hearts_J.png

            # Ajuste de ceros para números < 10 si el nombre del archivo lo requiere
            if simbolo.isdigit() and int(simbolo) < 10 and len(simbolo) == 1:
                simbolo_str = f"0{simbolo}"
            else:
                simbolo_str = simbolo

            filename = f"card_{pinta}_{simbolo_str}.png"
            path = os.path.join("Assets", "Blackjack", filename)

        if os.path.exists(path):
            return QPixmap(path)
        else:
            print(f"[UI] No se encontró imagen de carta: {path}")
            return QPixmap() # Retorna vacía


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
        # Usamos una clase interna personalizada para pintar
        self.area_juego = CanvasAviator(self)
        
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
        # Calcular tiempo t inverso desde el multiplicador para la animación,
        # o simplemente recibir t del backend.
        # Asumiendo M = 1 + (e^(0.55t) - 1) => M = e^(0.55t) => ln(M) = 0.55t => t = ln(M)/0.55
        if multiplicador > 0:
            try:
                t = math.log(multiplicador) / 0.55
            except ValueError:
                t = 0
        else:
            t = 0

        self.area_juego.actualizar_estado(t, multiplicador)
        self.boton_accion.setText(f"Retirar (${self.area_juego.multiplicador_actual * float(self.input_monto.text() or 0):.0f})")

    def iniciar_ronda(self) -> None:
        self.ronda_activa = True
        self.boton_accion.setText("Retirar")
        self.label_estado_ronda.setText("Ronda en Curso")
        self.area_juego.reset()

    def mostrar_crash(self, multiplicador_final: float) -> None:
        self.ronda_activa = False
        self.label_estado_ronda.setText(f"¡CRASH! {multiplicador_final:.2f}×")
        self.boton_accion.setText("Apostar")
        self.area_juego.crashear()


class CanvasAviator(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #2c3e50;") # Fondo oscuro estilo radar
        self.tiempo_actual = 0.0
        self.multiplicador_actual = 1.0
        self.crashed = False

        # Cargar imagen del avión
        self.pixmap_avion = QPixmap(p.RUTA_AVION)
        if self.pixmap_avion.isNull():
            print(f"[UI] Error cargando avión en {p.RUTA_AVION}")

    def actualizar_estado(self, tiempo, multiplicador):
        self.tiempo_actual = tiempo
        self.multiplicador_actual = multiplicador
        self.update() # Llama a paintEvent

    def reset(self):
        self.tiempo_actual = 0.0
        self.multiplicador_actual = 1.0
        self.crashed = False
        self.update()

    def crashear(self):
        self.crashed = True
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()

        # 1. Dibujar Ejes
        pen_ejes = QPen(QColor("white"), 2)
        painter.setPen(pen_ejes)
        painter.drawLine(40, h - 40, w - 20, h - 40) # Eje X
        painter.drawLine(40, h - 40, 40, 20)       # Eje Y

        # 2. Dibujar Curva
        # M(t) = e^(0.55t).
        # Mapeamos t (eje X) y M (eje Y) a coordenadas de pantalla.
        # Escala arbitraria para visualización:
        # X: 1 segundo = 30 pixeles
        # Y: 1x = 50 pixeles (desde abajo)

        scale_x = 30
        scale_y = 50
        origin_x = 40
        origin_y = h - 40

        path_points = []

        # Dibujamos desde t=0 hasta tiempo_actual
        # Paso de dibujo
        steps = int(self.tiempo_actual * 10) # 10 puntos por segundo
        if steps < 2: steps = 2

        prev_x = origin_x
        prev_y = origin_y

        pen_curva = QPen(QColor("#e74c3c"), 3) # Rojo
        painter.setPen(pen_curva)

        for i in range(steps + 1):
            t = (i / steps) * self.tiempo_actual
            if t < 0: t = 0

            # Ecuación: M = e^(0.55 * t)
            # Altura visual: (M - 1) * scale_y (para que empiece en el eje)
            m = math.exp(0.55 * t)

            x = origin_x + (t * scale_x)
            y = origin_y - ((m - 1) * scale_y)

            # Limitar a pantalla
            if x > w: x = w
            if y < 0: y = 0

            painter.drawLine(int(prev_x), int(prev_y), int(x), int(y))
            prev_x = x
            prev_y = y

        # 3. Dibujar Avión en la punta (prev_x, prev_y)
        if not self.pixmap_avion.isNull():
            # Centrar imagen en el punto
            offset_x = -self.pixmap_avion.width() // 2
            offset_y = -self.pixmap_avion.height() // 2
            painter.drawPixmap(int(prev_x + offset_x), int(prev_y + offset_y), self.pixmap_avion)

        # 4. Texto Multiplicador
        painter.setPen(QColor("white"))
        painter.setFont(QFont("Arial", 24, QFont.Bold))
        texto = f"{self.multiplicador_actual:.2f}x"
        if self.crashed:
            texto = f"CRASHED {texto}"
            painter.setPen(QColor("red"))

        painter.drawText(int(w/2) - 50, int(h/2), texto)