from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QLineEdit, 
                             QComboBox, QTableWidget, QHBoxLayout, QVBoxLayout, QGridLayout, QFrame,
                             QMessageBox, QHeaderView, QTableWidgetItem, QApplication, QTextEdit)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QRectF, QSize
from PyQt5.QtGui import QFont, QPixmap, QColor, QPainter, QPen, QPalette, QMovie
from os import path
import sys
import time

class VTienda(QWidget):
    cargar_tienda = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.menucin()
        
    def menucin(self):
        self.cargar_tienda.connect(self.show)
        self.setGeometry(1600, 500, 600, 400)
        self.setWindowTitle("Tienda!")
        self.setObjectName("RPGWindow") #nombre interno -not important
        #GUARDARCOMANDO MUYBUENO!  
        self.setStyleSheet("""
            #RPGWindow {
                background-color: #88E788; 
            }
            QLabel {
                color: black;
                font-family: "Verdana";
                font-size: 20px;
            }
            QPushButton {
                font-family: 'Algerian'; 
                font-size: 28px;
                background-color: #2c3e50;
                color: white;
                border: 4px solid #1a252f;
                border-radius: 8px;
            }
            QTextEdit {
                border: 4px solid #5c5c5c;
                border-radius: 10px;
                padding: 10px;
                background-color: #f0f0f0;
                font-family: "Cascadia Code";
            }
            #titulito {
                font-family: 'Algerian';
                font-size: 55px;
                color: black;
                font-weight: bold;
            }
        """) #Background el color y qlabel el color de los label en general
        
        
        
        self.titulotienda = QLabel(self)
        pathin = path.join("Fotos","Shop.gif")
        self.movie = QMovie(pathin)
        self.movie.setScaledSize(QSize(200,150))
        self.titulotienda.setMovie(self.movie) 
        self.movie.start()
        lay_tienda = QHBoxLayout()
        lay_tienda.addStretch(1)
        lay_tienda.addWidget(self.titulotienda)
        lay_tienda.addStretch(1)
        
        cartas = QHBoxLayout()
        self.carta1 = QLabel(self)
        self.carta2 = QLabel(self)
        self.carta3 = QLabel(self)
        cartas.addWidget(self.carta1)
        cartas.addStretch(1)
        cartas.addWidget(self.carta2)
        cartas.addStretch(1)
        cartas.addWidget(self.carta3)
        
        botoncitos = QHBoxLayout()
        self.volver = QPushButton("Volver a la tienda",self)
        self.volver.resize(self.volver.sizeHint())
        self.volver.clicked.connect(self.hide)
        botoncitos.addStretch(1)
        botoncitos.addWidget(self.volver)
        botoncitos.addStretch(2)
        self.reroll = QPushButton("Reroll! ($3)", self)
        self.reroll.resize(self.reroll.sizeHint())
        botoncitos.addWidget(self.reroll)
        botoncitos.addStretch(1)
        
        final = QVBoxLayout()
        final.addLayout(lay_tienda)
        final.addLayout(cartas)
        final.addLayout(botoncitos)
        self.setLayout(final) 
        
class VForja(QWidget):
    pass        
        
class VColeccion(QWidget):
    pass
        
        
if __name__ == "__main__":
    def hook(type, value, traceback) -> None:
        print(type)
        print(traceback)

    sys.__excepthook__ = hook

    app = QApplication([])

    ventana_1 = VTienda()

    ventana_1.show()
    
    sys.exit(app.exec())