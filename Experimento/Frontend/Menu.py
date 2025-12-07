from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QLineEdit, 
                             QComboBox, QTableWidget, QHBoxLayout, QVBoxLayout, QGridLayout, QFrame,
                             QMessageBox, QHeaderView, QTableWidgetItem, QApplication)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QRectF
from PyQt5.QtGui import QFont, QPixmap, QColor, QPainter, QPen, QPalette
from os import path
import sys
import time

class Menu(QWidget):
    cargar_menu = pyqtSignal()
    reabrir_inicio =pyqtSignal()  
    
    def __init__(self):
        super().__init__()
        self.init_gui()
    
    def init_gui(self):
        self.cargar_menu.connect(self.show)
        self.setGeometry(300, 400, 1000, 900)
        self.setObjectName("RPGWindow") #nombre interno -not important
        #GUARDARCOMANDO MUYBUENO!  
        self.setStyleSheet("""
            #RPGWindow {
                background-color: #060638; 
            }
            QLabel {
                color: white;
            }
        """) #Background el color y qlabel el color de los label en general
        self.setWindowTitle("Menu!")
        
        botonesly = QVBoxLayout()
        self.iniciar = QPushButton("Iniciar Ronda", self)
        self.iniciar.resize(self.iniciar.sizeHint())
        
        self.tienda = QPushButton("Tienda", self)
        self.tienda.resize(self.tienda.sizeHint())
        
        self.coleccion = QPushButton("Ver colección", self)
        self.coleccion.resize(self.coleccion.sizeHint())
        
        self.forja = QPushButton("Forja", self)
        self.forja.resize(self.forja.sizeHint())
        
        self.espiar = QPushButton("Espiar enemigo", self)
        self.espiar.resize(self.espiar.sizeHint())
        
        self.salir = QPushButton("Salir", self)
        self.salir.resize(self.salir.sizeHint())
        