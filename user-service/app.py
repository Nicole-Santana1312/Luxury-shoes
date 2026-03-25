"""
USER SERVICE - Puerto dinámico (Render)
Maneja: perfil de usuario, historial de ordenes
Base de datos: users.db (SQLite, se crea automaticamente)
Se comunica con: auth-service para verificar tokens
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import requests
import os

app = Flask(__name__)
CORS(app)

DB = "users.db"
AUTH_URL = os.environ.get("AUTH_URL")  # ← URL pública del auth-service en Render

# ── Crear tablas al iniciar ────────────────────────────────────
def init_db():
    conn = sqlite3.connect(DB)
    c    = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
            username TEXT PRIMARY KEY,
            email    TEXT DEFAULT '',
            address  TEXT DEFAULT ''
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            username   TEXT NOT NULL,
            items      TEXT NOT NULL,
            total      REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

init_db()

def verify_token(token):
    """Llama al auth-service para verificar si el token es valido"""
    try:
        r = requests.post(f"{AUTH_URL}/verify", json={"token": token}, timeout=5)
        if r.status_code == 200:
            return r.json().get("username")
    except requests.RequestException:
        pass
    return None

# ── Rutas ──────────────────────────────────────────────────────

@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "user-service"})

@app.route("/profile", methods=["GET"])
def get_profile():
    token    = request.headers.get("Authorization", "")
    username = verify_token(token)
    if not username:
        return jsonify({"error": "No autorizado"}), 401

    conn = sqlite3.connect(DB)
    c    = conn.cursor()
    c.execute("SELECT username, email, address FROM profiles WHERE username=?", (username,))
    row  = c.fetchone()
    conn.close()

    if not row:
        return jsonify({"username": username, "email": "", "address": ""})
    return jsonify({"username": row[0], "email": row[1], "address": row[2]})

@app.route("/profile", methods=["PUT"])
def update_profile():
    token    = request.headers.get("Authorization", "")
    username = verify_token(token)
    if not username:
        return jsonify({"error": "No autorizado"}), 401

    data    = request.get_json()
    email   = data.get("email", "")
    address = data.get("address", "")

    conn = sqlite3.connect(DB)
    c    = conn.cursor()
    c.execute("INSERT OR REPLACE INTO profiles (username, email, address) VALUES (?,?,?)",
              (username, email, address))
    conn.commit()
    conn.close()
    return jsonify({"message": "Perfil actualizado"})

@app.route("/orders", methods=["GET"])
def get_orders():
    token    = request.headers.get("Authorization", "")
    username = verify_token(token)
    if not username:
        return jsonify({"error": "No autorizado"}), 401

    conn = sqlite3.connect(DB)
    c    = conn.cursor()
    c.execute("""SELECT id, items, total, created_at FROM orders
                 WHERE username=? ORDER BY created_at DESC""", (username,))
    rows = c.fetchall()
    conn.close()

    orders = [{"id": r[0], "items": r[1], "total": r[2], "fecha": r[3]} for r in rows]
    return jsonify(orders)

@app.route("/orders", methods=["POST"])
def create_order():
    token    = request.headers.get("Authorization", "")
    username = verify_token(token)
    if not username:
        return jsonify({"error": "No autorizado"}), 401

    data  = request.get_json()
    items = data.get("items", "")
    total = data.get("total", 0)

    conn = sqlite3.connect(DB)
    c    = conn.cursor()
    c.execute("INSERT INTO orders (username, items, total) VALUES (?,?,?)",
              (username, items, total))
    conn.commit()
    conn.close()
    return jsonify({"message": "Orden registrada"}), 201


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)