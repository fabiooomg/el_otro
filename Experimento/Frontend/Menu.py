from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QLineEdit, 
                             QComboBox, QTableWidget, QHBoxLayout, QVBoxLayout, QGridLayout, QFrame,
                             QMessageBox, QHeaderView, QTableWidgetItem, QApplication, QTextEdit)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QRectF, QSize
from PyQt5.QtGui import QFont, QPixmap, QColor, QPainter, QPen, QPalette, QMovie
from os import path
import sys
import time

class Menu(QWidget):
    cargar_menu = pyqtSignal()
    reabrir_inicio =pyqtSignal()
    abre_tienda = pyqtSignal()  
    abre_coleccion= pyqtSignal()
    abre_forja = pyqtSignal() 
    abre_ronda = pyqtSignal() 
    senal_espia = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.init_gui()
    
    def init_gui(self):
        self.cargar_menu.connect(self.show)
        self.setGeometry(300, 400, 1200, 700)
        self.setObjectName("RPGWindow") #nombre interno -not important
        #GUARDARCOMANDO MUYBUENO!  
        self.setStyleSheet("""
            #RPGWindow {
                background-color: #B2FFFF; 
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
        
        """self.iniciar.clicked.connect()
        self.tienda.clicked.connect()
        self.coleccion.clicked.connect()
        self.forja.clicked.connect()
        self.espiar.clicked.connect()
        self.salir.clicked.connect()"""
        
        botonesly.addWidget(self.iniciar)
        botonesly.addWidget(self.tienda)
        botonesly.addWidget(self.coleccion)
        botonesly.addWidget(self.forja)
        botonesly.addWidget(self.espiar)
        botonesly.addWidget(self.salir)
        
        comunes = QVBoxLayout()
        self.nombre = QLabel("Nombre:",self)
        self.ronda = QLabel("Ronda: <b>1</b>", self) 
        self.oro = QLabel("Oro:", self)
        comunes.addStretch(3)
        comunes.addWidget(self.nombre)
        comunes.addWidget(self.ronda)
        comunes.addWidget(self.oro)
        comunes.addStretch(1)
        
        perfil = QHBoxLayout()
        self.gif = QLabel(self)
        camino = path.join("Fotos", "perfil.gif") 
        self.movie = QMovie(camino)
        self.movie.setScaledSize(QSize(250,250))
        self.gif.setMovie(self.movie)
        self.movie.start()
        perfil.addWidget(self.gif)
        perfil.addStretch(3)
        perfil.addLayout(comunes)
        
        desc = QVBoxLayout()
        self.editor =  QTextEdit()
        self.editor.setGeometry(0,0,650,800)
        desc.addStretch(1)
        desc.addWidget(self.editor)
        desc.addStretch(3)
        desc.addLayout(perfil)
        desc.addStretch(1)
        
        junta_todo = QHBoxLayout()
        junta_todo.addStretch(1)
        junta_todo.addLayout(botonesly)
        junta_todo.addStretch(5)
        junta_todo.addLayout(desc)
        junta_todo.addStretch(1)
        
        final = QVBoxLayout()
        self.titulo = QLabel("-Menu Principal-", self)
        self.titulo.setObjectName("titulito")
        final.addStretch(1)
        final.addWidget(self.titulo, alignment=Qt.AlignCenter)
        final.addStretch(2)
        final.addLayout(junta_todo)
        final.addStretch(1)
        
        self.setLayout(final)
        
    def abrir_menu(self, name="", oro=-1, ronda=-1):
        self.show()
        if name != "": 
            self.nombre.setText(f"Nombre: <b>{name}</b>")
            self.nombre.repaint()
        if ronda != -1:
            self.ronda.setText(f"Ronda: <b>{ronda}</b>")
            self.ronda.repaint()
        if oro != -1:
            self.oro.setText(f"Oro: <b>{oro}</b>")
            self.oro.repaint()
        
    def empezar_ronda(self):
        self.hide()
        self.empezar_ronda.emit()
    
    def abrir_tienda(self):
        self.hide()
        self.abre_tienda.emit()

    def abrir_coleccion(self):
        self.hide()
        self.abre_coleccion.emit()

    def abrir_forja(self):
        self.hide()
        self.abre_forja.emit()
        


if __name__ == "__main__":
    def hook(type, value, traceback) -> None:
        print(type)
        print(traceback)

    sys.__excepthook__ = hook

    app = QApplication([])

    ventana_1 = Menu()

    ventana_1.show()
    
    sys.exit(app.exec())