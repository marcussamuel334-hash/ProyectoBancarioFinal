
# PRÉSTAMOS: calcular intereses simples, cuotas y registrar créditos.

from datetime import date
from BaseDatos import conectar
from Utilidades import numero, aviso, error, tabla


def configurar(menu, actualizar):

    # Campos para ingresar los datos del préstamo.
    cliente = menu.comboBox_6
    cuenta = menu.comboBox_7
    monto = menu.lineEdit_19
    interes = menu.lineEdit_20
    cuotas = menu.lineEdit_21

    # Campos donde aparecen los resultados del cálculo.
    resultados = [
        menu.lineEdit_23,
        menu.lineEdit_24,
        menu.lineEdit_25,
        menu.lineEdit_26,
        menu.lineEdit_27
    ]

    # Copiar automáticamente los valores a los nuevos campos.
    # lineEdit_32 muestra lo mismo que lineEdit_23.
    menu.lineEdit_24.textChanged.connect(menu.lineEdit_32.setText)

    # lineEdit_33 muestra lo mismo que lineEdit_26.
    menu.lineEdit_26.textChanged.connect(menu.lineEdit_33.setText)

    # Mostrar los valores actuales al iniciar.
    menu.lineEdit_32.setText(menu.lineEdit_23.text())
    menu.lineEdit_33.setText(menu.lineEdit_26.text())

    # Evitar que los campos de copia se modifiquen manualmente.
    menu.lineEdit_32.setReadOnly(True)
    menu.lineEdit_33.setReadOnly(True)

    # CALCULAR PRÉSTAMO
    def calcular():

        # Obtener el monto solicitado.
        capital = numero(monto.text())

        # Obtener el interés y la cantidad de cuotas.
        tasa = float(interes.text())
        cantidad = int(cuotas.text())

        # Validar los datos.
        if tasa < 0 or cantidad <= 0:
            raise ValueError("Interés y cuotas no válidos.")

        # Calcular el total con interés simple.
        total = round(capital * (1 + tasa / 100), 2)

        # Calcular cuánto se pagará en cada cuota.
        pago = round(total / cantidad, 2)

        # Mostrar los resultados en los LineEdit.
        valores = [
            capital,
            capital * tasa / 100,
            total,
            pago,
            cantidad
        ]

        for campo, valor in zip(resultados, valores):
            campo.setText(str(round(valor, 2)))

        # lineEdit_32 y lineEdit_33 se actualizan automáticamente.

        return capital, tasa, cantidad, total, pago

    # BOTÓN CALCULAR
    def calcular_boton():
        try:
            calcular()
        except Exception as e:
            error(menu, e)

    # GUARDAR PRÉSTAMO
    def guardar():
        try:

            # Verificar que se seleccionó un cliente y una cuenta.
            if cliente.currentData() is None or cuenta.currentData() is None:
                raise ValueError("Seleccione cliente y cuenta.")

            # Calcular los valores del préstamo.
            capital, tasa, cantidad, total, pago = calcular()

            # Conectar con SQLite.
            with conectar() as db:

                # Verificar que la cuenta pertenece al cliente.
                d = db.execute(
                    "SELECT cliente_id FROM cuentas WHERE id=?",
                    (cuenta.currentData(),)
                ).fetchone()

                if not d or d[0] != cliente.currentData():
                    raise ValueError("La cuenta no pertenece al cliente.")

                # Registrar el préstamo.
                db.execute(
                    """INSERT INTO prestamos
                    (cliente_id, cuenta_id, monto, interes, cuotas,
                    total, cuota, fecha)
                    VALUES(?,?,?,?,?,?,?,?)""",
                    (
                        cliente.currentData(),
                        cuenta.currentData(),
                        capital,
                        tasa,
                        cantidad,
                        total,
                        pago,
                        menu.dateEdit_5.date().toString("yyyy-MM-dd")
                    )
                )

                # Agregar el préstamo al saldo de la cuenta.
                db.execute(
                    "UPDATE cuentas SET saldo=ROUND(saldo+?,2) WHERE id=?",
                    (capital, cuenta.currentData())
                )

                # Registrar el movimiento bancario.
                db.execute(
                    """INSERT INTO movimientos
                    (cuenta_id,tipo,monto,fecha,concepto)
                    VALUES(?,?,?,?,?)""",
                    (
                        cuenta.currentData(),
                        "Desembolso de préstamo",
                        capital,
                        date.today().isoformat(),
                        "Préstamo"
                    )
                )

            # Mostrar mensaje de confirmación.
            aviso(menu, "Préstamo registrado.")

            # Actualizar la información del sistema.
            actualizar()

        except Exception as e:
            error(menu, e)

    # LIMPIAR CAMPOS
    def limpiar():

        # Limpiar los campos de entrada y resultados.
        for campo in [monto, interes, cuotas] + resultados:
            campo.clear()

        # lineEdit_32 y lineEdit_33 también se limpian
        # automáticamente mediante textChanged.

    # MOSTRAR PRÉSTAMOS
    def listar():

        # Consultar los préstamos registrados.
        with conectar() as db:

            filas = db.execute(
                """SELECT
                p.id,
                c.nombre || ' ' || c.apellido,
                p.monto,
                p.interes,
                p.total,
                p.cuotas,
                (SELECT COUNT(*)
                 FROM pagos g
                 WHERE g.prestamo_id=p.id) AS pagadas
                FROM prestamos p
                JOIN clientes c ON c.id=p.cliente_id
                ORDER BY p.id DESC"""
            ).fetchall()

        activos = []
        cancelados = []

        # Separar los préstamos activos y cancelados.
        for f in filas:

            restante = f[5] - f[6]

            registro = (
                *f,
                restante,
                "Cancelado" if restante == 0 else "Activo"
            )

            if restante == 0:
                cancelados.append(registro)
            else:
                activos.append(registro)

        # Encabezados de las tablas.
        encabezados = [
            "ID",
            "Cliente",
            "Monto",
            "Interés %",
            "Total",
            "Cuotas",
            "Pagadas",
            "Pendientes",
            "Estado"
        ]

        # Mostrar los préstamos activos.
        tabla(menu.tableWidget_7, encabezados, activos)

        # Mostrar los préstamos cancelados.
        tabla(menu.tableWidget_8, encabezados, cancelados)

    # CONECTAR BOTONES

    # Calcular préstamo.
    menu.pushButton_28.clicked.connect(calcular_boton)

    # Guardar préstamo.
    menu.pushButton_29.clicked.connect(guardar)

    # Limpiar campos.
    menu.pushButton_30.clicked.connect(limpiar)

    # Regresar al inicio sin cerrar el programa.
    menu.pushButton_31.clicked.connect(
        lambda: menu.stackedWidget.setCurrentIndex(0)
    )

    # Actualizar préstamos activos.
    menu.pushButton_32.clicked.connect(listar)

    # Actualizar préstamos cancelados.
    menu.pushButton_33.clicked.connect(listar)

    # Cargar los préstamos al iniciar.
    listar()
