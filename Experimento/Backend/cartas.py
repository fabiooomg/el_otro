import numpy
from os import path

class Carta():
    
    def __init__(self):
        self.nombre = None
        self.tipo = None
        self.calidad = None
        self.oro = None
        self.objetivo = None
        
        
    def recibir_msj(self, diccionario:dict):
        pass
    
class Jugador():
    
    def __init__(self, nombre, dificultad):
        self.nombre = nombre
        self.dificultad = dificultad
        self.creararchivo()
        
    def creararchivo(self):
        self.archivo = path.join(f"Guardado", f"{self.nombre}")
        
