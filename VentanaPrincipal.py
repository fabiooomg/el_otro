from PyQt5.QtWidgets import QLabel, QApplication, QWidget, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QFileDialog, QTextEdit
import sys
from PyQt5.QtCore import pyqtSignal


class VentanaPrincipal(QWidget):

    senal_abrir_ventana_principal = pyqtSignal()
    senal_abrir_mapa = pyqtSignal()

    senal_cargar_datos = pyqtSignal(str) 
    
    def __init__(self, titulo: str) -> None:
        super().__init__()
        # Definimos lo básico de la ventana.
        self.setWindowTitle(titulo)
        self.setGeometry(300, 500, 800, 600)
        self.init_gui()

    def init_gui(self):
        self.ruta = "" 
        self.senal_abrir_ventana_principal.connect(self.show)
        self.botonmapa = QPushButton("&Boton de mapa", self)
        self.botonmapa.resize(self.botonmapa.sizeHint())
        self.botonmapa.clicked.connect(self.abrir_mapa)

        self.botonexec = QPushButton("&Ejecutar", self)
        self.botonexec.resize(self.botonexec.sizeHint())
        self.botonexec.clicked.connect(
            self.cargar_datos)  # Cambiar metodo a llamar

        box_botones = QVBoxLayout()
        box_botones.addStretch(1)
        box_botones.addWidget(self.botonexec)
        box_botones.addStretch(1)
        box_botones.addWidget(self.botonmapa)

        self.cuadroinput = QLineEdit('', self)
        self.cuadroinput.setGeometry(100, 100, 200, 80)

        self.botonabrir = QPushButton("&Selecciona un archivo....", self)
        self.botonabrir.resize(self.botonabrir.sizeHint())
        self.botonabrir.clicked.connect(self.abrir_darchivo)
        self.lbl_ruta = QLabel("Ruta del archivo: (ninguno)", self)

        box_filedialog = QHBoxLayout()
        box_filedialog.addStretch(2)
        box_filedialog.addWidget(self.lbl_ruta)
        box_filedialog.addStretch(1)
        box_filedialog.addWidget(self.botonabrir)
        box_filedialog.addStretch(2)
        box_filedialog.addWidget(self.cuadroinput)

        self.editor_texto = QTextEdit()
        self.editor_texto.setGeometry(0, 0, 300, 600)
        contenido_largo = "No lo implemente upsi\n" + " \n" * 100
        self.editor_texto.setText(contenido_largo)
        self.editor_texto.repaint()
        box_scroll = QVBoxLayout()
        box_scroll.addWidget(self.editor_texto)

        self.minilabel = QLabel("Output:",self) 
        
        box_filescroll = QVBoxLayout()
        box_filescroll.addLayout(box_filedialog)
        box_filescroll.addWidget(self.minilabel)
        box_filescroll.addLayout(box_scroll)

        box_final = QHBoxLayout()
        box_final.addLayout(box_filescroll)
        box_final.addStretch(3)
        box_final.addLayout(box_botones)

        self.setLayout(box_final)

    def abrir_mapa(self) -> None:
        self.hide()
        self.senal_abrir_mapa.emit()

    def abrir_darchivo(self):
        ruta, _ = QFileDialog.getOpenFileName(
            self,
            "Abrir un Archivo",
            "",
            "Todos los archivos (*.*)"
        )
        if ruta:
            # Si el usuario seleccionó un archivo y no canceló
            self.lbl_ruta.setText(f"Ruta del archivo: {ruta}")
            self.lbl_ruta.repaint()
            self.ruta = ruta 
            print(f"Archivo seleccionado: {ruta}")
        else:
            # Si el usuario presionó 'Cancelar'
            self.ruta = ""
            self.lbl_ruta.setText("Ruta del archivo: Cancelado")
            self.lbl_ruta.repaint()
            print("Selección cancelada.")
            
    def cargar_datos(self):
        texto = self.cuadroinput.text()
        if texto != "" and self.ruta != "":
            self.senal_cargar_datos.emit(texto, self.ruta)
        else:
            self.senal_cargar_datos.emit("", "")

    def actualizar_scroll(self, texto: str):
        self.editor_texto.setText(texto)
        self.editor_texto.repaint()
    


if __name__ == '__main__':
    def hook(type, value, traceback) -> None:
        print(type)
        print(traceback)

    sys.__excepthook__ = hook

    app = QApplication([])

    ventana_1 = VentanaPrincipal("Principal")

    ventana_1.show()
    sys.exit(app.exec())
