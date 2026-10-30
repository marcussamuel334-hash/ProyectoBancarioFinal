# PROYECTO BANCARIO EN PYTHON + QT DESIGNER + SQLITE.
import os
os.environ['QT_ENABLE_HIGHDPI_SCALING'] = '0'
os.environ['QT_SCALE_FACTOR'] = '1'

import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMessageBox, QPushButton
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, Qt, QDate

from BaseDatos import conectar, iniciar
from Autenticacion import PerroLogin
from Utilidades import llenar
import Clientes, Cuentas, Movimientos, Prestamos, Pagos, Historial

app = QApplication(sys.argv)
# Cuando es .exe, las Perros .ui están al lado de Banco.exe.
# En VS Code, están al lado de Main.py.
carpeta = Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).resolve().parent
os.chdir(carpeta)  # Para cargar las imágenes de las Perros .ui por ruta relativa.
iniciar()  # Crea banco.db sin borrar datos anteriores.


def cargar(nombre):
    # Carga un archivo de Qt Designer, si existe.
    archivo = QFile(str(carpeta / nombre))
    if not archivo.open(QFile.ReadOnly):
        return None
    Perro = QUiLoader().load(archivo)
    archivo.close()
    return Perro


menu = cargar('Menu2.ui')
if menu is None:
    QMessageBox.critical(None, 'Error', 'No se encontró o no se pudo abrir Menu2.ui.')
    sys.exit(1)

menu.setWindowTitle('Sistema de Administración Bancaria')
menu.setWindowFlag(Qt.WindowMaximizeButtonHint, False)
menu.setFixedSize(menu.size())  # Conservar tamaño de Qt Designer.

# Establecer las fechas actuales al iniciar, no fechas antiguas predeterminadas.
for nombre in ['dateEdit', 'dateEdit_2', 'dateEdit_3', 'dateEdit_4',
               'dateEdit_5', 'dateEdit_6', 'dateEdit_7', 'dateEdit_8',
               'dateEdit_10']:
    getattr(menu, nombre).setDate(QDate.currentDate())
menu.dateEdit_9.setDate(QDate(2000, 1, 1))  # Historial desde el año 2000.

# Los montos y conceptos de transferencias se conectan a sus campos reales:
# lineEdit_18: monto (a la altura de "Monto")
# lineEdit_16: concepto (a la altura de "Concepto")
menu.lineEdit_18.clear()  # Qt Designer mostraba incorrectamente "Monto:" dentro.
for nombre in ['lineEdit_12', 'lineEdit_15', 'lineEdit_18']:
    getattr(menu, nombre).setPlaceholderText('Ingrese el monto')
for nombre in ['lineEdit_13', 'lineEdit_14', 'lineEdit_16']:
    getattr(menu, nombre).setPlaceholderText('Escriba el concepto')

# Navegación del menú lateral.
botones = [
    ('BTTINICIO1', 0), ('BTTCLIENTES1', 1), ('BTTCUENTEABANCARIA1', 2),
    ('BTTDEPOSITO1', 3), ('BTTRETIRO1', 4), ('BTTTRASFERENCIA1', 5),
    ('BTTPRESTAMOSYCREDITOS1', 6), ('BTTPAGOSDECUOTAS1', 7),
    ('BTTHISTORIAL1', 8), ('BTTREPORTE1', 9),
    ('BTTCLIENTES2', 1), ('BTTCUENTEABANCARIA2', 2),
    ('BTTDEPOSITO2', 3), ('BTTRETIRO2', 4), ('BTTTRASFERENCIA2', 5),
    ('BTTPRESTAMOSYCREDITOS2', 6), ('BTTPAGOSDECUOTAS2', 7),
    ('BTTHISTORIAL2', 8), ('BTTREPORTE2', 9)
]
for nombre, pagina in botones:
    boton = getattr(menu, nombre, None)
    if boton is not None:
        boton.clicked.connect(lambda checked=False, p=pagina:
                              menu.stackedWidget.setCurrentIndex(p))

menu.stackedWidget.setCurrentIndex(0)

# Las siguientes funciones se asignan cuando los módulos están preparados.
mostrar_cuentas = lambda: None
listar_prestamos = lambda: None
mostrar_movimientos = lambda: None


def actualizar():
    # Actualizar los nombres y números en todas las listas desplegables.
    with conectar() as db:
        clientes = db.execute(
            "SELECT id,nombre||' '||apellido FROM clientes ORDER BY nombre"
        ).fetchall()
        cuentas = db.execute('''
            SELECT c.id, 'Cuenta '||c.id||' - '||cl.nombre||' '||cl.apellido
                   ||' ('||c.tipo||')'
            FROM cuentas c JOIN clientes cl ON cl.id=c.cliente_id ORDER BY c.id
        ''').fetchall()
        prestamos = db.execute(
            "SELECT id,'Crédito '||id FROM prestamos ORDER BY id DESC"
        ).fetchall()

    combos_clientes = [menu.comboBox, menu.comboBox_6, menu.comboBox_8,
                       menu.comboBox_10, menu.comboBox_14]
    combos_cuentas = [menu.comboBox_3, menu.comboBox_4, menu.comboBox_5,
                      menu.comboBox_13, menu.comboBox_7]
    for combo in combos_clientes:
        seleccion = combo.currentData()
        llenar(combo, clientes, 'Seleccionar cliente' if combo in
               [menu.comboBox, menu.comboBox_6] else 'Todos los clientes')
        posicion = combo.findData(seleccion)
        if seleccion is not None and posicion >= 0:
            combo.setCurrentIndex(posicion)

    for combo in combos_cuentas:
        seleccion = combo.currentData()
        llenar(combo, cuentas, 'Seleccionar cuenta')
        posicion = combo.findData(seleccion)
        if seleccion is not None and posicion >= 0:
            combo.setCurrentIndex(posicion)

    seleccion = menu.comboBox_11.currentData()
    llenar(menu.comboBox_11, prestamos, 'Seleccionar crédito')
    posicion = menu.comboBox_11.findData(seleccion)
    if seleccion is not None and posicion >= 0:
        menu.comboBox_11.setCurrentIndex(posicion)

    menu.comboBox_15.clear()
    menu.comboBox_15.addItems(['Todos', 'Depósito', 'Retiro', 'Transferencia',
                               'Transferencia recibida', 'Depósito inicial',
                               'Desembolso de préstamo'])
    mostrar_cuentas()
    listar_prestamos()
    mostrar_movimientos()


# Conectar formularios con la base de datos.
Clientes.configurar(menu, actualizar)
Cuentas.configurar(menu, actualizar)
mostrar_movimientos = Movimientos.configurar(menu, actualizar)
Prestamos.configurar(menu, actualizar)
Pagos.configurar(menu, actualizar)
Historial.configurar(menu)
mostrar_cuentas = lambda: menu.lineEdit_10.textChanged.emit(menu.lineEdit_10.text())
listar_prestamos = lambda: menu.pushButton_32.click()
actualizar()


# INICIO DE SESIÓN NUEVO: el primer usuario se crea al iniciar.
def acceso_correcto():
    # Se oculta el login y se abre el menú bancario.
    login.hide()
    menu.show()


login = PerroLogin(acceso_correcto)


def cerrar_sesion():
    # El usuario sale del sistema sin cerrar el programa.
    menu.hide()
    login.mostrar()


for nombre in ['BTTCERRAR1', 'BTTCERRAR2']:
    boton = getattr(menu, nombre, None)
    if boton is not None:
        boton.clicked.connect(cerrar_sesion)


# CARÁTULA INICIAL: tú crearás Caratula.ui usando Qt Designer.
# Pon al botón el objectName BTTCONTINUAR.
# Acepta el nombre en minúsculas o con mayúscula inicial.
caratula = cargar('caratula.ui') or cargar('Caratula.ui')


def abrir_login():
    # Cerrar la carátula y mostrar el formulario de usuario y contraseña.
    if caratula is not None:
        caratula.hide()
    login.mostrar()


if caratula is not None:
    caratula.setWindowTitle('Presentación - Sistema Bancario')
    continuar = caratula.findChild(QPushButton, 'BTTCONTINUAR')
    if continuar is None:
        QMessageBox.warning(None, 'Carátula',
            'Tu caratula.ui necesita un botón con objectName BTTCONTINUAR. '
            'Por ahora se abrirá el inicio de sesión.')
        abrir_login()
    else:
        continuar.clicked.connect(abrir_login)
        caratula.show()
else:
    # Permite probar el programa antes de que diseñes Caratula.ui.
    abrir_login()

sys.exit(app.exec())
