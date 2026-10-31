    # PAGOS DE CUOTAS: registrar cuotas y mostrar cuántas faltan.
from datetime import date,timedelta
from BaseDatos import conectar
from Utilidades import aviso,error,tabla,llenar

def configurar(menu,actualizar):
    credito=menu.comboBox_11
    cuota=menu.lineEdit_22
    metodo=menu.comboBox_12
    fecha=menu.dateEdit_8
    vista=menu.tableWidget_9
    campos=[menu.lineEdit_28,menu.lineEdit_31,menu.lineEdit_30,menu.lineEdit_29]

    def mostrar():
        codigo=credito.currentData()
        if codigo is None:
            tabla(vista,['N°','Fecha límite','Monto','Estado'],[])
            for c in campos:c.clear()
            cuota.clear()
            return
        with conectar() as db:
            p=db.execute('SELECT total,cuotas,cuota,fecha FROM prestamos WHERE id=?',(codigo,)).fetchone()
            pagos=db.execute('SELECT numero_cuota,fecha,monto FROM pagos WHERE prestamo_id=?',(codigo,)).fetchall()
        if not p:return
        pagadas={f[0]:f for f in pagos}
        filas=[];atrasadas=0
        inicio=date.fromisoformat(p[3])
        for n in range(1,p[1]+1):
            # Fecha aproximada: cuotas mensuales cada 30 días (demostración).
            limite=inicio+timedelta(days=30*n)
            estado='Pagada' if n in pagadas else ('Atrasada' if limite<date.today() else 'Pendiente')
            if estado=='Atrasada':atrasadas+=1
            filas.append((n,limite.isoformat(),round(p[0]-p[2]*(p[1]-1),2) if n==p[1] else p[2],estado))
        tabla(vista,['Cuota','Fecha límite','Monto','Estado'],filas)
        for c,v in zip(campos,[p[1],len(pagadas),p[1]-len(pagadas),atrasadas]):c.setText(str(v))
        # Mostrar el monto exacto de la siguiente cuota pendiente.
        siguiente = next((i for i in range(1, p[1] + 1) if i not in pagadas), None)
        if siguiente is None:
            cuota.clear()
        else:
            cantidad = round(p[0]-p[2]*(p[1]-1),2) if siguiente==p[1] else p[2]
            cuota.setText(f'{cantidad:.2f}')

    def guardar():
        try:
            codigo=credito.currentData()
            if codigo is None:raise ValueError('Seleccione un crédito.')
            with conectar() as db:
                p=db.execute('SELECT total,cuotas,cuota FROM prestamos WHERE id=?',(codigo,)).fetchone()
                pagadas=[r[0] for r in db.execute('SELECT numero_cuota FROM pagos WHERE prestamo_id=?',(codigo,))]
                n=next((i for i in range(1,p[1]+1) if i not in pagadas),None)
                if n is None:raise ValueError('El crédito ya está cancelado.')
                cantidad=round(p[0]-p[2]*(p[1]-1),2) if n==p[1] else p[2]
                # No ignorar el monto escrito por el usuario.
                escrito=float(cuota.text().strip())
                if round(escrito, 2)!=round(cantidad, 2):
                    raise ValueError(f'La cuota pendiente debe ser Q {cantidad:.2f}.')
                db.execute('INSERT INTO pagos(prestamo_id,numero_cuota,monto,fecha,metodo) VALUES(?,?,?,?,?)',
                    (codigo,n,cantidad,fecha.date().toString('yyyy-MM-dd'),metodo.currentText()))
            aviso(menu,f'Cuota {n} registrada por Q {cantidad:.2f}.');mostrar();actualizar()
        except Exception as e:error(menu,e)

    def limpiar():
        cuota.clear();credito.setCurrentIndex(0);mostrar()

    credito.currentIndexChanged.connect(mostrar)
    menu.pushButton_34.clicked.connect(guardar)
    menu.pushButton_35.clicked.connect(limpiar)
    mostrar()
