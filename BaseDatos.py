# BASE DE DATOS SQLITE: almacena la información aunque se cierre el programa.
import sqlite3
from pathlib import Path
RUTA = Path(__file__).with_name('banco.db')

def conectar():
    # Abrir la base de datos y activar las relaciones entre tablas.
    db = sqlite3.connect(RUTA)
    db.execute('PRAGMA foreign_keys=ON')
    return db

def iniciar():
    # Crear las tablas solamente si todavía no existen.
    with conectar() as db:
        db.executescript('''
        CREATE TABLE IF NOT EXISTS clientes (
          id INTEGER PRIMARY KEY AUTOINCREMENT, dpi TEXT UNIQUE NOT NULL,
          nombre TEXT NOT NULL, apellido TEXT NOT NULL, telefono TEXT,
          correo TEXT, direccion TEXT, nacimiento TEXT);
        CREATE TABLE IF NOT EXISTS cuentas (
          id INTEGER PRIMARY KEY AUTOINCREMENT, cliente_id INTEGER NOT NULL,
          tipo TEXT NOT NULL, saldo REAL NOT NULL DEFAULT 0 CHECK(saldo>=0),
          FOREIGN KEY(cliente_id) REFERENCES clientes(id));
        CREATE TABLE IF NOT EXISTS movimientos (
          id INTEGER PRIMARY KEY AUTOINCREMENT, cuenta_id INTEGER NOT NULL,
          tipo TEXT NOT NULL, monto REAL NOT NULL CHECK(monto>0),
          fecha TEXT NOT NULL, concepto TEXT, destino_id INTEGER,
          FOREIGN KEY(cuenta_id) REFERENCES cuentas(id));
        CREATE TABLE IF NOT EXISTS prestamos (
          id INTEGER PRIMARY KEY AUTOINCREMENT, cliente_id INTEGER NOT NULL,
          cuenta_id INTEGER NOT NULL, monto REAL NOT NULL, interes REAL NOT NULL,
          cuotas INTEGER NOT NULL, total REAL NOT NULL, cuota REAL NOT NULL,
          fecha TEXT NOT NULL, FOREIGN KEY(cliente_id) REFERENCES clientes(id),
          FOREIGN KEY(cuenta_id) REFERENCES cuentas(id));
        CREATE TABLE IF NOT EXISTS pagos (
          id INTEGER PRIMARY KEY AUTOINCREMENT, prestamo_id INTEGER NOT NULL,
          numero_cuota INTEGER NOT NULL, monto REAL NOT NULL, fecha TEXT NOT NULL,
          metodo TEXT, FOREIGN KEY(prestamo_id) REFERENCES prestamos(id),
          UNIQUE(prestamo_id,numero_cuota));
        ''')
