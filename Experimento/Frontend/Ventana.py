from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QLineEdit, 
                             QComboBox, QTableWidget, QHBoxLayout, QVBoxLayout, QGridLayout, QFrame,
                             QMessageBox, QHeaderView, QTableWidgetItem, QApplication)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QRectF
from PyQt5.QtGui import QFont, QPixmap, QColor, QPainter, QPen, QPalette
from os import path
import sys
import time

class Ventanita(QWidget):
    reinsertar_name = pyqtSignal()
    abrir_main = pyqtSignal() 
     
    def __init__(self):
        super().__init__()
        self.init_gui()
    
    def init_gui(self):
        self.reinsertar_name.connect(self.show)
        self.setGeometry(300, 400, 800, 600)
        self.setObjectName("RPGWindow") #nombre interno -not important
        #GUARDARCOMANDO MUYBUENO!  
        self.setStyleSheet("""
            #RPGWindow {
                background-color: #404040; 
            }
            QLabel {
                color: white;
            }
        """) #Background el color y qlabel el color de los label en general

        self.setWindowTitle("Ventanita")
        
        self.titulo = QLabel("<b>UN RPG</b>", self)
        self.titulo.setFont(QFont("Algerian", 24))
        
        self.autor = QLabel("by: <b>Fabio Condori</b>", self)
        self.autor.setFont(QFont("Algerian", 10))

        self.foto_logo = QLabel(self)
        camino = path.join("Fotos", "caballero.jpg")
        pixmap = QPixmap(camino) 
        self.foto_logo.setPixmap(pixmap.scaled(200,200, Qt.KeepAspectRatio))
        
        linea = QFrame()
        linea.setFrameShape(QFrame.HLine)
        linea.setFrameShadow(QFrame.Raised) 
        linea.setStyleSheet("background-color: darkgray;")
        
        layout = QVBoxLayout(linea)
        layout.addWidget(self.titulo, alignment=Qt.AlignCenter)
        layout.addWidget(self.autor, alignment=Qt.AlignCenter)
        layout.addWidget(self.foto_logo, alignment=Qt.AlignCenter)
        layout.addStretch(3)
        
        self.nombre = QLabel("Ingresa tu nombre:", self)
        self.nombre.setFont(QFont("Verdana"))
        self.input = QLineEdit(self)
        self.confirmar = QPushButton("Confirmar", self) 
        self.confirmar.resize(self.confirmar.sizeHint())
        self.confirmar.clicked.connect(self.procesar_nombre)
        
        midlayout = QHBoxLayout()
        midlayout.addWidget(self.input)
        midlayout.addWidget(self.confirmar)  
        
        layout.addWidget(self.nombre)
        layout.addLayout(midlayout)
        layout.addStretch(3)
        
        self.minilabel = QLabel("", self)
        layout.addWidget(self.minilabel)
        
        self.setLayout(layout)
    
    def procesar_nombre(self):
        texto = self.input.text()
        if texto != "":
            self.minilabel.setText(f"Bienvenido {texto}! Estas entrando al juego espera un segundo...")
            self.minilabel.repaint()
            time.sleep(2)
            self.cambiar_ventana()
        else:
            self.minilabel.setText("No has ingresado tu nombre!")
            self.minilabel.repaint()
    
    def cambiar_ventana(self):
        self.hide()
        self.abrir_main.emit()
        
        
        
if __name__ == "__main__":
    def hook(type, value, traceback) -> None:
        print(type)
        print(traceback)

    sys.__excepthook__ = hook

    app = QApplication([])

    ventana_1 = Ventanita()

    ventana_1.show()
    
    sys.exit(app.exec())