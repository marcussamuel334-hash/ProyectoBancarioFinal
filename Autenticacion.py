# AUTENTICACIÓN: permite crear un usuario y entrar sin claves fijas en el código.
import hashlib
import hmac
import os

from PySide6.QtWidgets import (QWidget, QLabel, QLineEdit, QPushButton,
                               QVBoxLayout, QMessageBox, QDialog, QDialogButtonBox,
                               QFormLayout)
from PySide6.QtCore import QTimer
from BaseDatos import conectar


def preparar_usuarios():
    # Crear la tabla sin modificar clientes, cuentas o movimientos.
    with conectar() as db:
        db.execute('''CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE NOT NULL,
            sal BLOB NOT NULL,
            clave_hash BLOB NOT NULL)''')


def hay_usuarios():
    with conectar() as db:
        return db.execute('SELECT COUNT(*) FROM usuarios').fetchone()[0] > 0


def verificar(nombre, clave):
    # Comprobar la contraseña sin guardarla como texto.
    with conectar() as db:
        fila = db.execute('SELECT sal,clave_hash FROM usuarios WHERE nombre=?',
                          (nombre,)).fetchone()
    if not fila:
        return False
    sal, clave_hash = fila
    intento = hashlib.pbkdf2_hmac('sha256', clave.encode('utf-8'), sal, 260000)
    return hmac.compare_digest(intento, clave_hash)


class ArchivoLogin(QWidget):
    def __init__(self, entrar_al_menu):
        super().__init__()
        preparar_usuarios()
        self.entrar_al_menu = entrar_al_menu
        self.setWindowTitle('Sistema Bancario - Acceso')
        self.setFixedSize(410, 280)

        layout = QVBoxLayout(self)
        titulo = QLabel('SISTEMA DE ADMINISTRACIÓN BANCARIA')
        titulo.setStyleSheet('font-size: 16px; font-weight: bold;')
        layout.addWidget(titulo)
        layout.addWidget(QLabel('Iniciar sesión'))

        self.usuario = QLineEdit()
        self.usuario.setPlaceholderText('Nombre de usuario')
        layout.addWidget(self.usuario)

        self.clave = QLineEdit()
        self.clave.setPlaceholderText('Contraseña')
        self.clave.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.clave)

        boton = QPushButton('Ingresar')
        boton.clicked.connect(self.ingresar)
        self.clave.returnPressed.connect(self.ingresar)
        layout.addWidget(boton)
        layout.addWidget(QLabel('Si es la primera vez, podrás crear tu usuario.'))

    def mostrar(self):
        self.clave.clear()
        self.show()
        self.usuario.setFocus()
        # Registrar al usuario al abrir por primera vez, no antes de la carátula.
        if not hay_usuarios():
            QTimer.singleShot(0, self.crear_primer_usuario)

    def crear_primer_usuario(self):
        if hay_usuarios():
            return
        dialogo = QDialog(self)
        dialogo.setWindowTitle('Configurar el primer usuario')
        formulario = QFormLayout(dialogo)
        nombre = QLineEdit()
        clave = QLineEdit()
        repetir = QLineEdit()
        clave.setEchoMode(QLineEdit.EchoMode.Password)
        repetir.setEchoMode(QLineEdit.EchoMode.Password)
        formulario.addRow('Usuario:', nombre)
        formulario.addRow('Contraseña:', clave)
        formulario.addRow('Repetir contraseña:', repetir)
        botones = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok |
                                    QDialogButtonBox.StandardButton.Cancel)
        formulario.addRow(botones)

        def guardar():
            nuevo = nombre.text().strip()
            if not nuevo:
                QMessageBox.warning(dialogo, 'Atención', 'Escribe un nombre de usuario.')
                return
            if len(clave.text()) < 8:
                QMessageBox.warning(dialogo, 'Atención', 'Utiliza una contraseña de 8 caracteres o más.')
                return
            if clave.text() != repetir.text():
                QMessageBox.warning(dialogo, 'Atención', 'Las contraseñas no coinciden.')
                return
            sal = os.urandom(16)
            clave_hash = hashlib.pbkdf2_hmac('sha256', clave.text().encode('utf-8'), sal, 260000)
            with conectar() as db:
                db.execute('INSERT INTO usuarios(nombre,sal,clave_hash) VALUES(?,?,?)',
                           (nuevo, sal, clave_hash))
            self.usuario.setText(nuevo)
            dialogo.accept()

        botones.accepted.connect(guardar)
        botones.rejected.connect(dialogo.reject)
        if dialogo.exec() == QDialog.DialogCode.Accepted:
            QMessageBox.information(self, 'Usuario creado',
                                    'Cuenta creada. Ingresa con tu nueva contraseña.')

    def ingresar(self):
        nombre = self.usuario.text().strip()
        if verificar(nombre, self.clave.text()):
            self.clave.clear()
            self.entrar_al_menu()
        else:
            QMessageBox.warning(self, 'Atención', 'Usuario o contraseña incorrectos.')
            self.clave.clear()
