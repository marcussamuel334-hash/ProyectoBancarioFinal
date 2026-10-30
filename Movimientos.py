# DEPÓSITOS, RETIROS Y TRANSFERENCIAS.
# Cada botón ejecuta su propia operación y no modifica el tipo de movimiento.
from BaseDatos import conectar
from Utilidades import numero, aviso, error, tabla


def configurar(menu, actualizar):
    operaciones = [
        # Tipo, cuenta de origen, destino, monto, fecha, concepto, guardar, limpiar, tabla
        ('Depósito', menu.comboBox_3, None, menu.lineEdit_12,
         menu.dateEdit_2, menu.lineEdit_13, menu.pushButton_23,
         menu.pushButton_22, menu.tableWidget_3),
        ('Retiro', menu.comboBox_4, None, menu.lineEdit_15,
         menu.dateEdit_3, menu.lineEdit_14, menu.pushButton_25,
         menu.pushButton_24, menu.tableWidget_4),
        ('Transferencia', menu.comboBox_5, menu.comboBox_13, menu.lineEdit_18,
         menu.dateEdit_4, menu.lineEdit_16, menu.pushButton_27,
         menu.pushButton_26, menu.tableWidget_5)
    ]

    consultas = []

    for tipo, origen, destino, monto, fecha, concepto, guardar, limpiar, vista in operaciones:

        # Creamos una función independiente para cada pantalla.
        def preparar(tipo, origen, destino, monto, fecha, concepto, guardar, limpiar, vista):
            def mostrar():
                with conectar() as db:
                    filas = db.execute('''
                        SELECT fecha, cuenta_id, printf('Q %.2f', monto), concepto
                        FROM movimientos WHERE tipo=?
                        ORDER BY id DESC LIMIT 100
                    ''', (tipo,)).fetchall()
                tabla(vista, ['Fecha', 'Cuenta', 'Monto', 'Concepto'], filas)

            def limpiar_campos():
                # Vaciar solo los campos de la operación seleccionada.
                monto.clear()
                concepto.clear()

            def registrar():
                try:
                    origen_id = origen.currentData()
                    destino_id = destino.currentData() if destino is not None else None

                    if origen_id is None:
                        raise ValueError('Seleccione la cuenta de origen.')

                    cantidad = numero(monto.text().strip())
                    descripcion = concepto.text().strip()

                    if tipo == 'Transferencia':
                        if destino_id is None:
                            raise ValueError('Seleccione la cuenta de destino.')
                        if destino_id == origen_id:
                            raise ValueError('No puede transferir a la misma cuenta.')

                    dia = fecha.date().toString('yyyy-MM-dd')

                    # SQLite guarda ambos saldos y movimientos en una sola transacción.
                    # Si algo falla, deshace todos los cambios.
                    with conectar() as db:
                        cuenta = db.execute(
                            'SELECT saldo FROM cuentas WHERE id=?', (origen_id,)
                        ).fetchone()
                        if cuenta is None:
                            raise ValueError('La cuenta de origen no existe.')

                        if tipo != 'Depósito' and round(cuenta[0], 2) < cantidad:
                            raise ValueError('Saldo insuficiente.')

                        if tipo == 'Transferencia':
                            existe = db.execute(
                                'SELECT id FROM cuentas WHERE id=?', (destino_id,)
                            ).fetchone()
                            if existe is None:
                                raise ValueError('La cuenta de destino no existe.')

                        # Depósito suma al saldo; retiro y transferencia restan.
                        cambio = cantidad if tipo == 'Depósito' else -cantidad
                        db.execute(
                            'UPDATE cuentas SET saldo=ROUND(saldo+?, 2) WHERE id=?',
                            (cambio, origen_id)
                        )
                        db.execute('''
                            INSERT INTO movimientos
                            (cuenta_id, tipo, monto, fecha, concepto, destino_id)
                            VALUES (?, ?, ?, ?, ?, ?)
                        ''', (origen_id, tipo, cantidad, dia, descripcion, destino_id))

                        if tipo == 'Transferencia':
                            # Abonar a la cuenta destinataria y registrar la recepción.
                            db.execute(
                                'UPDATE cuentas SET saldo=ROUND(saldo+?, 2) WHERE id=?',
                                (cantidad, destino_id)
                            )
                            db.execute('''
                                INSERT INTO movimientos
                                (cuenta_id, tipo, monto, fecha, concepto, destino_id)
                                VALUES (?, ?, ?, ?, ?, ?)
                            ''', (destino_id, 'Transferencia recibida', cantidad,
                                  dia, descripcion or ('Desde cuenta ' + str(origen_id)),
                                  origen_id))

                    limpiar_campos()
                    actualizar()
                    mostrar()
                    aviso(menu, tipo + ' realizado correctamente.' if tipo == 'Depósito'
                          else tipo + ' realizado correctamente.' if tipo == 'Retiro'
                          else 'Transferencia realizada correctamente.')
                except Exception as e:
                    error(menu, e)

            # clicked envía un booleano. La lambda impide que reemplace argumentos.
            guardar.clicked.connect(lambda checked=False: registrar())
            limpiar.clicked.connect(lambda checked=False: limpiar_campos())
            mostrar()
            return mostrar

        consultas.append(preparar(tipo, origen, destino, monto, fecha,
                                  concepto, guardar, limpiar, vista))

    def refrescar():
        # Actualizar las tres tablas después de una operación.
        for consultar in consultas:
            consultar()

    return refrescar
