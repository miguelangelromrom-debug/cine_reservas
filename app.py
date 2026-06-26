"""
=============================================================
  SIMULADOR DE RESERVA DE ASIENTOS - CINE "MATRIX FILMS"
  Materia: Programación / Estructuras de Datos
  Tema: Matrices (Arreglos Bidimensionales)
=============================================================
"""

from flask import Flask, render_template, jsonify, request, session

# --- Inicialización de la aplicación Flask ---
app = Flask(__name__)
app.secret_key = "cine_matrix_secret_2024"  # Necesario para usar session (datos de sesión del usuario)

# -------------------------------------------------------
# CONSTANTE: Tamaño de la sala (5 filas x 5 columnas)
# -------------------------------------------------------
FILAS = 5
COLUMNAS = 5


def crear_sala():
    """
    Crea y retorna una MATRIZ 5x5 llena de ceros.
    Cada 0 representa un asiento LIBRE.
    Estructura:
        sala[fila][columna] = 0  → Libre
        sala[fila][columna] = 1  → Ocupado
    """
    # Comprensión de lista: genera una lista de 5 listas, cada una con 5 ceros
    return [[0 for _ in range(COLUMNAS)] for _ in range(FILAS)]


def obtener_sala():
    """
    Obtiene la sala actual desde la sesión del usuario.
    Si no existe aún, crea una nueva sala vacía y la guarda en session.
    Esto permite que cada usuario tenga su propia sala independiente.
    """
    if "sala" not in session:
        session["sala"] = crear_sala()
    return session["sala"]


# -------------------------------------------------------
#  RUTA PRINCIPAL: Muestra la página del simulador
# -------------------------------------------------------
@app.route("/")
def index():
    """Renderiza el template principal con la sala actual."""
    sala = obtener_sala()  # Obtiene o crea la sala de la sesión
    return render_template("index.html", sala=sala, filas=FILAS, columnas=COLUMNAS)


# -------------------------------------------------------
#  RUTA API: Reservar un asiento (método POST)
# -------------------------------------------------------
@app.route("/reservar", methods=["POST"])
def reservar():
    """
    Recibe la fila y columna por JSON (AJAX desde el navegador),
    verifica si el asiento está libre y lo reserva si corresponde.

    Retorna un JSON con:
        - success: True/False
        - mensaje: Texto informativo para mostrar al usuario
        - sala: Estado actualizado de toda la matriz
    """
    datos = request.get_json()          # Leer los datos JSON enviados desde JavaScript
    fila = datos.get("fila")            # Número de fila (0-indexado)
    columna = datos.get("columna")      # Número de columna (0-indexado)

    sala = obtener_sala()  # Obtener la sala desde la sesión

    # --- VALIDACIÓN 1: Coordenadas dentro del rango válido ---
    if not (0 <= fila < FILAS and 0 <= columna < COLUMNAS):
        return jsonify({
            "success": False,
            "mensaje": "Coordenadas inválidas. Fuera de rango."
        })

    # --- VALIDACIÓN 2: Verificar si el asiento ya está ocupado ---
    if sala[fila][columna] == 1:
        # El asiento ya fue reservado → mostrar error
        return jsonify({
            "success": False,
            "mensaje": f"❌ Asiento [{fila+1},{columna+1}] ya está RESERVADO."
        })

    # --- RESERVA: El asiento está libre → cambiamos 0 por 1 ---
    sala[fila][columna] = 1            # Marcar como ocupado
    session["sala"] = sala             # Guardar cambios en la sesión
    session.modified = True            # Indicar a Flask que la sesión fue modificada

    return jsonify({
        "success": True,
        "mensaje": f"✅ Asiento [{fila+1},{columna+1}] reservado exitosamente.",
        "sala": sala                   # Enviar la matriz actualizada al frontend
    })


# -------------------------------------------------------
#  RUTA API: Reiniciar la sala (liberar todos los asientos)
# -------------------------------------------------------
@app.route("/reiniciar", methods=["POST"])
def reiniciar():
    """
    Restaura la sala a su estado inicial: todos los asientos en 0 (libres).
    Útil para demostrar el concepto de reinicialización de la matriz.
    """
    session["sala"] = crear_sala()     # Crear una nueva sala vacía
    session.modified = True
    return jsonify({
        "success": True,
        "mensaje": "🔄 Sala reiniciada. Todos los asientos están libres.",
        "sala": session["sala"]
    })


# -------------------------------------------------------
#  RUTA API: Obtener estado actual de la sala
# -------------------------------------------------------
@app.route("/estado")
def estado():
    """Retorna el estado actual de la matriz en formato JSON."""
    sala = obtener_sala()
    ocupados = sum(sala[f][c] for f in range(FILAS) for c in range(COLUMNAS))
    libres = FILAS * COLUMNAS - ocupados
    return jsonify({
        "sala": sala,
        "ocupados": ocupados,
        "libres": libres,
        "total": FILAS * COLUMNAS
    })


# -------------------------------------------------------
#  PUNTO DE ENTRADA: Ejecutar el servidor Flask
# -------------------------------------------------------
if __name__ == "__main__":
    # debug=True → recarga automática al guardar cambios (útil en desarrollo)
    app.run(debug=True, port=5000)
