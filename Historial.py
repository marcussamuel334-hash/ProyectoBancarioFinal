# HISTORIAL: consultar movimientos financieros por cliente y fecha.
from BaseDatos import conectar
from Utilidades import tabla

def configurar(menu):
    def consultar():
        cliente=menu.comboBox_14.currentData()
        tipo=menu.comboBox_15.currentText()
        desde=menu.dateEdit_9.date().toString('yyyy-MM-dd')
        hasta=menu.dateEdit_10.date().toString('yyyy-MM-dd')
        sql='''SELECT m.fecha,cl.nombre||' '||cl.apellido,m.cuenta_id,m.tipo,m.monto,m.concepto
          FROM movimientos m JOIN cuentas c ON c.id=m.cuenta_id
          JOIN clientes cl ON cl.id=c.cliente_id WHERE m.fecha BETWEEN ? AND ?'''
        datos=[desde,hasta]
        if cliente is not None:sql+=' AND cl.id=?';datos.append(cliente)
        if tipo not in ('Todos','Todas','Tipos de operación','Seleccionar'):
            sql+=' AND m.tipo=?';datos.append(tipo)
        sql+=' ORDER BY m.fecha DESC,m.id DESC'
        with conectar() as db:filas=db.execute(sql,datos).fetchall()
        tabla(menu.tableWidget_10,['Fecha','Cliente','Cuenta','Tipo','Monto','Concepto'],filas)
    menu.pushButton_36.clicked.connect(consultar)
    return consultar
