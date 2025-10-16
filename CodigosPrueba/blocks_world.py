import collections
from queue import LifoQueue

class BlockWorld:
    def __init__(self, Bloques: list):
        self.garra = LifoQueue()
        self.bloques = Bloques

def tomar_bloque(blocksworld, bloque_tomar):
    pass

def dejar_bloque():
    pass

class Menu:
    def __init__(self, nombre, blocksworld: BlockWorld):
        self.nombre = nombre
        self.blocksworld = blocksworld
    
    def flujo
    
    def menu_principal(self):
        while True:
            opcion = input(f"""
Menu Principal: Blocks World
Jugador: {self.jugador}

Opciones:
[1] Empezar juego
[2] Cambiar nombre
[3] Cambiar Bloques
[4] Cerrar juego
""")
            if opcion not in "1234":
                print("Ingresa una opcion valida (1,2,3,4)")
            elif opcion == "1":
                input("Una vez ingresado al juego no puedes salir...")
                opcion_final = input("Estas seguro? [Si]/[No]")
                ñ*-