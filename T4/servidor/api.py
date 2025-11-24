import flask
from flask import Flask, request, jsonify
import json
import time
import os
import threading
import parametros as p  # Asume que aquí están las rutas y constantes

app = Flask(__name__)

# ==========================================================
# GESTIÓN DE CONCURRENCIA (REEMPLAZO DE CSV LOCK)
# ==========================================================

# Lock global para asegurar que solo un hilo acceda a los archivos a la vez
USERS_LOCK = threading.Lock()
GAMES_LOCK = threading.Lock()

# ==========================================================
# MANEJO DE ARCHIVOS (REEMPLAZO DE LIBRERÍA CSV)
# ==========================================================

def _read_users_data() -> list[dict]:
    """ Lee el archivo de usuarios y devuelve una lista de diccionarios. """
    users_data = []
    # Asegura que el archivo exista, sino, lo crea vacío
    if not os.path.exists(p.USUARIOS_PATH):
        return [] 
        
    with USERS_LOCK: # 🔒 Bloquear el acceso al archivo
        try:
            with open(p.USUARIOS_PATH, mode='r', encoding='utf-8') as file:
                for line in file:
                    # Formato esperado: usuario,clave,saldo,conectado
                    row = line.strip().split(',')
                    if len(row) == 4:
                        users_data.append({
                            "usuario": row[0].strip(),
                            "clave": row[1].strip(),
                            "saldo": int(row[2].strip()),
                            "conectado": bool(row[3].strip() == 'True') # Convertir a booleano
                        })
        except Exception as e:
            print(f"Error leyendo usuarios: {e}")
            # En caso de error, es mejor no devolver datos corruptos
            return [] 
    return users_data

def _write_users_data(users_data: list[dict]) -> None:
    """ Escribe toda la lista de diccionarios de usuarios de vuelta al archivo. """
    with USERS_LOCK: # 🔒 Bloquear el acceso al archivo
        try:
            with open(p.USUARIOS_PATH, mode='w', encoding='utf-8') as file:
                for user in users_data:
                    line = f"{user['usuario']},{user['clave']},{user['saldo']},{user['conectado']}\n"
                    file.write(line)
        except Exception as e:
            print(f"Error escribiendo usuarios: {e}")

# ==========================================================
# AUTENTICACIÓN (Middleware)
# ==========================================================

def token_requerido(func):
    """ Decorador para verificar el TOKEN_AUTENTICACION en los headers. """
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        # Asume que el token se encuentra en p.TOKEN_AUTENTICACION
        if auth_header == p.TOKEN_AUTENTICACION:
            return func(*args, **kwargs)
        else:
            return flask.Response(
                json.dumps({"error": "Token de autenticación inválido"}),
                status=401,
                mimetype='application/json'
            )
    # Importante: Renombrar la función para que Flask la distinga
    wrapper.__name__ = func.__name__ 
    return wrapper

# ==========================================================
# ENDPOINTS PÚBLICOS
# ==========================================================

# (Público) GET /users/<user_id> 
@app.route('/users/<string:user_id>', methods=['GET'])
def get_user(user_id):
    """ Verifica si el usuario existe, valida la clave y retorna su saldo. """
    # Intentar obtener la clave del cuerpo de la petición
    data = request.get_json(silent=True)
    clave_input = data.get("clave") if data else None

    users_data = _read_users_data()
    for user in users_data:
        if user["usuario"] == user_id:
            # Verificar contraseña si se proporciona
            if clave_input is not None and user["clave"] != clave_input:
                return flask.Response(
                    json.dumps({"error": "Contraseña incorrecta"}),
                    status=401, # Unauthorized
                    mimetype='application/json'
                )

            return flask.Response(
                json.dumps({"usuario": user_id, "saldo": user["saldo"]}),
                status=200,
                mimetype='application/json'
            )
    
    return flask.Response(
        json.dumps({"error": "Usuario no encontrado"}),
        status=404,
        mimetype='application/json'
    )

# (Público) POST /register 
@app.route('/register', methods=['POST'])
def register():
    """ Registra un nuevo usuario con saldo inicial. """
    data = request.get_json()
    usuario = data.get("usuario")
    clave = data.get("clave") # Asume que la clave se pasa en el JSON
    
    if not usuario or not clave:
        return flask.Response(
            json.dumps({"error": "Faltan datos de usuario o clave"}),
            status=400,
            mimetype='application/json'
        )

    users_data = _read_users_data()
    # 1. Verificar si ya existe
    if any(user["usuario"] == usuario for user in users_data):
        return flask.Response(
            json.dumps({"error": "El usuario ya existe"}),
            status=409, # Conflict
            mimetype='application/json'
        )

    # 2. Agregar nuevo usuario a la lista en memoria
    new_user = {
        "usuario": usuario,
        "clave": clave,
        "saldo": p.SALDO_INICIAL,
        "conectado": False
    }
    users_data.append(new_user)

    # 3. Reescribir el archivo completo
    _write_users_data(users_data)
    
    return flask.Response(
        json.dumps({"mensaje": "Registro exitoso", "saldo": p.SALDO_INICIAL}),
        status=201, # Created
        mimetype='application/json'
    )

# ==========================================================
# ENDPOINTS PRIVADOS (Requerir Token del Servidor)
# ==========================================================

# (Privado) PATCH /users/<user_id>
@app.route('/users/<string:user_id>', methods=['PATCH'])
@token_requerido
def update_saldo(user_id):
    """ Modifica el saldo de un usuario (+ para ganar, - para apostar). """
    data = request.get_json()
    cambio_saldo = data.get("cambio_saldo", 0) # Debe ser un entero positivo o negativo
    
    if not isinstance(cambio_saldo, int):
        return flask.Response(
            json.dumps({"error": "El cambio de saldo debe ser un entero"}),
            status=400,
            mimetype='application/json'
        )

    users_data = _read_users_data()
    usuario_encontrado = False
    nuevo_saldo = -1

    # 1. Buscar y actualizar saldo en memoria
    for user in users_data:
        if user["usuario"] == user_id:
            usuario_encontrado = True
            if user["saldo"] + cambio_saldo < 0:
                # Evitar saldos negativos (doble chequeo)
                return flask.Response(
                    json.dumps({"error": "Saldo insuficiente"}),
                    status=403, # Forbidden
                    mimetype='application/json'
                )
            
            user["saldo"] += cambio_saldo
            nuevo_saldo = user["saldo"]
            break

    if not usuario_encontrado:
        return flask.Response(
            json.dumps({"error": "Usuario no encontrado"}),
            status=404,
            mimetype='application/json'
        )
    
    # 2. Reescribir el archivo completo con el cambio
    _write_users_data(users_data)

    return flask.Response(
        json.dumps({"mensaje": "Saldo actualizado", "nuevo_saldo": nuevo_saldo}),
        status=200,
        mimetype='application/json'
    )

# (Privado) GET /games/historial
@app.route('/games/historial', methods=['GET'])
@token_requerido
def get_historial():
    """ Retorna el historial de ganancias/pérdidas globales. """
    historial = []
    if not os.path.exists(p.GANANCIAS_PATH):
        return flask.Response(
            json.dumps({"historial": []}),
            status=200,
            mimetype='application/json'
        )

    # Lectura del historial de juegos
    with GAMES_LOCK:
        try:
            with open(p.GANANCIAS_PATH, mode='r', encoding='utf-8') as file:
                for line in file:
                    # Formato esperado: id_partida,nombre_usuario,timestamp,monto
                    row = line.strip().split(',')
                    if len(row) == 4:
                        historial.append({
                            "id_partida": row[0].strip(),
                            "usuario": row[1].strip(),
                            "timestamp": float(row[2].strip()),
                            "monto": int(row[3].strip())
                        })
        except Exception as e:
            return flask.Response(
                json.dumps({"error": f"Error leyendo historial: {str(e)}"}),
                status=500, 
                mimetype='application/json'
            )

    # El historial debe ser retornado ordenado (normalmente por timestamp)
    # y solo se debe enviar el TOP N (si el front-end lo pide)
    # Aquí retornamos todo el historial para simplicidad.
    return flask.Response(
        json.dumps({"historial": historial}),
        status=200,
        mimetype='application/json'
    )


# (Privado) POST /games/<juego_especifico>
@app.route('/games/<string:juego_especifico>', methods=['POST'])
@token_requerido
def log_results(juego_especifico):
    """ Registra los resultados de una ronda de juego. """
    # Se espera que el servidor envíe en el body los resultados por jugador
    # Ejemplo: [{"usuario": "Juan", "monto": 100}, ...]
    data = request.get_json()
    
    if not isinstance(data, list):
        return flask.Response(
            json.dumps({"error": "Datos inválidos, se espera una lista de resultados"}),
            status=400,
            mimetype='application/json'
        )
    
    # id_partida: Usa el primer caracter del juego (A, B) para el prefijo de ID
    prefijo_id = juego_especifico[0].upper() if juego_especifico else 'X'

    with GAMES_LOCK: # Bloquear al escribir
        try:
            # Usar 'a' (append) para escribir solo las nuevas líneas, es más eficiente
            with open(p.GANANCIAS_PATH, mode='a', encoding='utf-8') as file:
                for resultado in data:
                    # Formato: id_partida, nombre_usuario, timestamp, monto
                    usuario = resultado.get("usuario")
                    monto = resultado.get("monto", 0)

                    if usuario and isinstance(monto, (int, float)):
                        line = f"{prefijo_id}-{int(time.time())},{usuario},{time.time()},{int(monto)}\n"
                        file.write(line)
                    else:
                        print(f"Error en el formato de resultado: {resultado}")

            return flask.Response(
                json.dumps({"mensaje": "Resultados guardados"}),
                status=200, mimetype='application/json'
            )

        except Exception as e:
            return flask.Response(
                json.dumps({"error": f"Error al guardar resultados: {str(e)}"}),
                status=500, mimetype='application/json'
            )

# ==========================================================
# FUNCIÓN DE INICIO
# ==========================================================

def iniciar_api(host, port):
    """ Función para iniciar Flask en un thread. """
    # Deshabilitar el logging de Flask si es necesario para mantener la terminal limpia
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    
    app.run(host=host, port=port, debug=False)