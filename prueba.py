tablero = [] 
for i in range(10):
    tablero.append([])
    for j in range(10):
        tablero[i].append("-")
        
tablero[3][5] = "B" 
tablero[5][8] = "B" 

def bomba_cruz(tablero:list, fila:int, columna:int, magnitud:int):
    for y in range(fila-magnitud,fila+magnitud+1):
       if 9 >= y >= 0:
            if tablero[y][columna] == "B":
                   tablero[y][columna] = "D"
            else:
                tablero[y][columna] = "X" 
                
    for x in range(columna-magnitud,columna+magnitud+1):
       if 9 >= x >= 0:
            if tablero[fila][x] == "B":
                   tablero[fila][x] = "D"
            else:
                tablero[fila][x] = "X" 
    return tablero

tablero = bomba_cruz(tablero, 5,5,2) 
for lista in tablero:
    print(lista)