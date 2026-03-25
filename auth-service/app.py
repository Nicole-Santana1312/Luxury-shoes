"""
AUTH SERVICE - Puerto 5001
Maneja: registro, login, verificacion de tokens
Base de datos: auth.db (SQLite, se crea automaticamente)
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import hashlib
import secrets

app = Flask(__name__)
CORS(app)

DB = "auth.db"

# ── Crear tablas al iniciar ────────────────────────────────────
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT    NOT NULL UNIQUE,
            password TEXT    NOT NULL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS tokens (
            token    TEXT PRIMARY KEY,
            username TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

def hash_pwd(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest()

# ── Rutas ──────────────────────────────────────────────────────

@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "auth-service", "puerto": 5001})

@app.route("/register", methods=["POST"])
def register():
    data     = request.get_json()
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    if not username or not password:
        return jsonify({"error": "Usuario y contraseña requeridos"}), 400

    conn = sqlite3.connect(DB)
    c    = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                  (username, hash_pwd(password)))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"error": "El usuario ya existe"}), 409
    conn.close()
    return jsonify({"message": "Usuario registrado"}), 201

@app.route("/login", methods=["POST"])
def login():
    data     = request.get_json()
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    conn = sqlite3.connect(DB)
    c    = conn.cursor()
    c.execute("SELECT id FROM users WHERE username=? AND password=?",
              (username, hash_pwd(password)))
    row = c.fetchone()

    if not row:
        conn.close()
        return jsonify({"error": "Usuario o contraseña incorrectos"}), 401

    token = secrets.token_hex(32)
    c.execute("INSERT OR REPLACE INTO tokens (token, username) VALUES (?, ?)",
              (token, username))
    conn.commit()
    conn.close()
    return jsonify({"token": token, "username": username}), 200

@app.route("/verify", methods=["POST"])
def verify():
    data  = request.get_json()
    token = data.get("token", "")

    conn = sqlite3.connect(DB)
    c    = conn.cursor()
    c.execute("SELECT username FROM tokens WHERE token=?", (token,))
    row  = c.fetchone()
    conn.close()

    if not row:
        return jsonify({"valid": False}), 401
    return jsonify({"valid": True, "username": row[0]}), 200

@app.route("/logout", methods=["POST"])
def logout():
    data  = request.get_json()
    token = data.get("token", "")

    conn = sqlite3.connect(DB)
    c    = conn.cursor()
    c.execute("DELETE FROM tokens WHERE token=?", (token,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Sesion cerrada"}), 200

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
