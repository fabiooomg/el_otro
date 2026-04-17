numeros = int(input())
lista = [] 
contador = 0 
suma = 0 

while contador < len(str(numeros)):
    lista.append(str(numeros)[contador])
    contador = contador + 1
    suma = suma + int(lista[-1])
    print(lista) 
    print(suma)