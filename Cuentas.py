# MÓDULO CUENTAS BANCARIAS.
from BaseDatos import conectar
from Utilidades import aviso,error,tabla,llenar

def configurar(menu, actualizar):
    cliente=menu.comboBox
    tipo=menu.comboBox_2
    numero=menu.lineEdit_8
    saldo=menu.lineEdit_9
    buscar=menu.lineEdit_10
    vista=menu.tableWidget_2

    def mostrar():
        filtro='%'+buscar.text().strip()+'%'
        with conectar() as db:
            filas=db.execute('''SELECT c.id,cl.nombre||' '||cl.apellido,c.tipo,printf('%.2f',c.saldo)
             FROM cuentas c JOIN clientes cl ON cl.id=c.cliente_id
             WHERE CAST(c.id AS TEXT) LIKE ? OR cl.nombre LIKE ? ORDER BY c.id''',(filtro,filtro)).fetchall()
        tabla(vista,['Cuenta','Cliente','Tipo','Saldo'],filas)

    def limpiar():
        numero.clear();saldo.clear();cliente.setCurrentIndex(0);mostrar()

    def guardar():
        try:
            if cliente.currentData() is None: raise ValueError('Seleccione un cliente.')
            monto=float(saldo.text() or 0)
            if monto<0: raise ValueError('El saldo no puede ser negativo.')
            with conectar() as db:
                cur=db.execute('INSERT INTO cuentas(cliente_id,tipo,saldo) VALUES(?,?,?)',
                    (cliente.currentData(),tipo.currentText(),monto))
                if monto>0:
                    db.execute('INSERT INTO movimientos(cuenta_id,tipo,monto,fecha,concepto) VALUES(?,?,?,?,?)',
                      (cur.lastrowid,'Depósito inicial',monto,__import__('datetime').date.today().isoformat(),'Apertura'))
            aviso(menu,'Cuenta creada.');limpiar();actualizar()
        except Exception as e:error(menu,e)

    def modificar():
        try:
            if not numero.text().isdigit():raise ValueError('Seleccione una cuenta.')
            if cliente.currentData() is None:raise ValueError('Seleccione un cliente.')
            # El saldo no se modifica aquí: se cambia con depósitos o retiros.
            with conectar() as db: db.execute('UPDATE cuentas SET cliente_id=?,tipo=? WHERE id=?',
               (cliente.currentData(),tipo.currentText(),int(numero.text())))
            aviso(menu,'Cuenta actualizada.');limpiar();actualizar()
        except Exception as e:error(menu,e)

    def eliminar():
        try:
            if not numero.text().isdigit():raise ValueError('Seleccione una cuenta.')
            with conectar() as db:
                cuenta=db.execute('SELECT saldo FROM cuentas WHERE id=?',(int(numero.text()),)).fetchone()
                if not cuenta or cuenta[0]!=0:raise ValueError('Solo puede eliminar cuentas con saldo cero.')
                db.execute('DELETE FROM cuentas WHERE id=?',(int(numero.text()),))
            aviso(menu,'Cuenta eliminada.');limpiar();actualizar()
        except Exception as e:error(menu,'No se puede eliminar una cuenta con movimientos o préstamos. '+str(e))

    def seleccionar(fila,columna):
        item=vista.item(fila,0)
        if not item:return
        with conectar() as db:
            d=db.execute('SELECT id,cliente_id,tipo,saldo FROM cuentas WHERE id=?',(item.text(),)).fetchone()
        if d:
            numero.setText(str(d[0]));cliente.setCurrentIndex(cliente.findData(d[1]))
            tipo.setCurrentText(d[2]);saldo.setText(str(d[3]))

    menu.pushButton_19.clicked.connect(guardar)
    menu.pushButton_18.clicked.connect(modificar)
    menu.pushButton_20.clicked.connect(eliminar)
    menu.pushButton_21.clicked.connect(limpiar)
    buscar.textChanged.connect(mostrar)
    vista.cellClicked.connect(seleccionar)
    mostrar()
