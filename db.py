import sqlite3
import os

DB_PATH = "data/cruz_automation.db"

def get_connection():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL, email TEXT, whatsapp TEXT,
        servicio TEXT NOT NULL, mensualidad REAL NOT NULL,
        fecha_pago TEXT, estado TEXT DEFAULT 'activo',
        notas TEXT, fecha_registro TEXT DEFAULT (date('now')))""")
    c.execute("""CREATE TABLE IF NOT EXISTS pagos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER, monto REAL NOT NULL,
        fecha TEXT DEFAULT (date('now')),
        metodo TEXT DEFAULT 'transferencia', notas TEXT,
        FOREIGN KEY (cliente_id) REFERENCES clientes(id))""")
    c.execute("""CREATE TABLE IF NOT EXISTS contenido_generado (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER, tipo TEXT, nicho TEXT,
        contenido TEXT, fecha TEXT DEFAULT (datetime('now')))""")
    c.execute("""CREATE TABLE IF NOT EXISTS tendencias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titulo TEXT, descripcion TEXT, oportunidad TEXT,
        fecha TEXT DEFAULT (datetime('now')))""")
    c.execute("""CREATE TABLE IF NOT EXISTS metas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mes TEXT, meta_ingresos REAL, meta_clientes INTEGER)""")
    conn.commit()
    conn.close()

def agregar_cliente(nombre, email, whatsapp, servicio, mensualidad, fecha_pago, estado, notas):
    conn = get_connection()
    conn.execute("INSERT INTO clientes (nombre, email, whatsapp, servicio, mensualidad, fecha_pago, estado, notas) VALUES (?,?,?,?,?,?,?,?)",
                 (nombre, email, whatsapp, servicio, mensualidad, fecha_pago, estado, notas))
    conn.commit()
    conn.close()

def obtener_clientes():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM clientes ORDER BY fecha_registro DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def actualizar_estado_cliente(cliente_id, nuevo_estado):
    conn = get_connection()
    conn.execute("UPDATE clientes SET estado=? WHERE id=?", (nuevo_estado, cliente_id))
    conn.commit()
    conn.close()

def eliminar_cliente(cliente_id):
    conn = get_connection()
    conn.execute("DELETE FROM clientes WHERE id=?", (cliente_id,))
    conn.commit()
    conn.close()

def registrar_pago(cliente_id, monto, fecha, metodo, notas):
    conn = get_connection()
    conn.execute("INSERT INTO pagos (cliente_id, monto, fecha, metodo, notas) VALUES (?,?,?,?,?)",
                 (cliente_id, monto, fecha, metodo, notas))
    conn.commit()
    conn.close()

def obtener_pagos():
    conn = get_connection()
    rows = conn.execute("""SELECT p.*, c.nombre as cliente_nombre
        FROM pagos p LEFT JOIN clientes c ON p.cliente_id = c.id
        ORDER BY p.fecha DESC""").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def ingresos_del_mes(mes):
    conn = get_connection()
    row = conn.execute("SELECT COALESCE(SUM(monto),0) as total FROM pagos WHERE strftime('%Y-%m', fecha)=?", (mes,)).fetchone()
    conn.close()
    return row["total"]

def guardar_contenido(cliente_id, tipo, nicho, contenido):
    conn = get_connection()
    conn.execute("INSERT INTO contenido_generado (cliente_id, tipo, nicho, contenido) VALUES (?,?,?,?)",
                 (cliente_id, tipo, nicho, contenido))
    conn.commit()
    conn.close()

def obtener_contenido():
    conn = get_connection()
    rows = conn.execute("""SELECT cg.*, c.nombre as cliente_nombre
        FROM contenido_generado cg LEFT JOIN clientes c ON cg.cliente_id = c.id
        ORDER BY cg.fecha DESC LIMIT 50""").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def guardar_tendencia(titulo, descripcion, oportunidad):
    conn = get_connection()
    conn.execute("INSERT INTO tendencias (titulo, descripcion, oportunidad) VALUES (?,?,?)",
                 (titulo, descripcion, oportunidad))
    conn.commit()
    conn.close()

def obtener_tendencias():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM tendencias ORDER BY fecha DESC LIMIT 20").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def guardar_meta(mes, meta_ingresos, meta_clientes):
    conn = get_connection()
    existing = conn.execute("SELECT id FROM metas WHERE mes=?", (mes,)).fetchone()
    if existing:
        conn.execute("UPDATE metas SET meta_ingresos=?, meta_clientes=? WHERE mes=?", (meta_ingresos, meta_clientes, mes))
    else:
        conn.execute("INSERT INTO metas (mes, meta_ingresos, meta_clientes) VALUES (?,?,?)", (mes, meta_ingresos, meta_clientes))
    conn.commit()
    conn.close()

def obtener_meta(mes):
    conn = get_connection()
    row = conn.execute("SELECT * FROM metas WHERE mes=?", (mes,)).fetchone()
    conn.close()
    return dict(row) if row else {"meta_ingresos": 2500, "meta_clientes": 10}
