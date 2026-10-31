# FUNCIONES QUE SE REPITEN EN VARIOS MÓDULOS.
from PySide6.QtWidgets import QMessageBox, QTableWidgetItem

def aviso(ventana, mensaje):
    # Mostrar un mensaje de información.
    QMessageBox.information(ventana, 'Banco', mensaje)

def error(ventana, mensaje):
    # Mostrar un error sin cerrar el programa.
    QMessageBox.warning(ventana, 'Atención', str(mensaje))

def numero(texto):
    # Convertir un monto escrito a número; no aceptar cero o negativos.
    valor = round(float(texto), 2)
    if valor <= 0:
        raise ValueError('El monto debe ser mayor que cero.')
    return valor

def tabla(widget, titulos, filas):
    # Mostrar los registros en una tabla de Qt Designer.
    widget.setColumnCount(len(titulos))
    widget.setHorizontalHeaderLabels(titulos)
    widget.setRowCount(len(filas))
    for i, fila in enumerate(filas):
        for j, dato in enumerate(fila):
            widget.setItem(i, j, QTableWidgetItem(str(dato if dato is not None else '')))

def llenar(combo, filas, titulo='Seleccionar'):
    # Guardar el ID real en cada opción del ComboBox.
    combo.clear()
    combo.addItem(titulo, None)
    for codigo, nombre in filas:
        combo.addItem(str(nombre), codigo)
