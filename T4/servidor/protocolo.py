import json
import struct
from math import ceil
import parametros as p # Contiene CLAVE_CASINO y CHUNK_SIZE

# ==========================================================
# Funciones de Cifrado
# ==========================================================

def cifrar_xor(paquete: bytes) -> bytes:
    """ Aplica el cifrado/descifrado XOR al paquete de 128 bytes. """
    cifrado = bytearray()
    clave = p.CLAVE_CASINO  # 128 bytes
    
    for i, byte in enumerate(paquete):
        # Asegura que la clave se repita si el paquete es más grande
        cifrado.append(byte ^ clave[i % len(clave)])
    
    return bytes(cifrado)


# ==========================================================
# Funciones de Envío (Empaquetado)
# ==========================================================

def empaquetar_mensaje(mensaje: dict) -> list[bytes]:
    """
    Serializa un mensaje JSON y lo fragmenta, enumera y encripta
    siguiendo el protocolo DCCasino.
    Retorna una lista de paquetes encriptados listos para enviar.
    """
    bytes_contenido = json.dumps(mensaje).encode("utf-8")
    largo_contenido = len(bytes_contenido)
    
    paquetes_a_enviar = []
    
    # 1. Prefijo de largo (4 bytes LITTLE ENDIAN)
    prefijo_largo = largo_contenido.to_bytes(4, "little")
    paquetes_a_enviar.append(prefijo_largo) # Es el primer elemento de la lista

    # 2. Fragmentación, Relleno, Enumeración y Encriptación
    for i in range(0, largo_contenido, p.CHUNK_SIZE):
        chunk = bytes_contenido[i:i + p.CHUNK_SIZE]
        
        # Relleno (Padding)
        if len(chunk) < p.CHUNK_SIZE:
            chunk += b'\x00' * (p.CHUNK_SIZE - len(chunk))

        # Enumeración (4 bytes BIG ENDIAN)
        indice_bytes = i.to_bytes(4, "big") 
        paquete = indice_bytes + chunk 
        
        # Encriptación XOR
        paquete_encriptado = cifrar_xor(paquete)
        paquetes_a_enviar.append(paquete_encriptado)

    return paquetes_a_enviar


# ==========================================================
# Funciones de Recepción (Desempaquetado)
# ==========================================================

def desencriptar_y_reasamblar(largo_contenido: int, paquetes_recibidos: dict) -> dict:
    """
    Toma los paquetes recibidos (índice: chunk) y reconstruye el mensaje.
    """
    contenido_reasamblado = bytearray()
    
    # 1. Reensamblar contenido en orden
    for indice in sorted(paquetes_recibidos.keys()):
        contenido_reasamblado.extend(paquetes_recibidos[indice])
    
    # 2. Recortar el relleno (padding)
    bytes_mensaje = bytes(contenido_reasamblado[:largo_contenido])

    # 3. JSON LOAD
    try:
        mensaje = json.loads(bytes_mensaje.decode("utf-8"))
        return mensaje
    except json.JSONDecodeError:
        return {"comando": "error", "data": "Mensaje JSON inválido"}