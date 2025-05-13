import logging
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import (
    ContextTypes, CommandHandler, Application
)

from config import COMPRAS_FILE, PROCESO_FILE, GASTOS_FILE, VENTAS_FILE
from utils.db import read_from_csv
from utils.helpers import format_currency

# Logger
logger = logging.getLogger(__name__)

async def reporte_general(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Genera un reporte general de todas las operaciones"""
    # Leer datos
    compras = read_from_csv(COMPRAS_FILE)
    procesos = read_from_csv(PROCESO_FILE)
    gastos = read_from_csv(GASTOS_FILE)
    ventas = read_from_csv(VENTAS_FILE)
    
    if not compras and not procesos and not gastos and not ventas:
        await update.message.reply_text(
            "No hay datos registrados para generar un reporte."
        )
        return
    
    # Calcular totales
    total_compras = sum(float(compra.get('total', 0)) for compra in compras)
    total_kg_comprados = sum(float(compra.get('cantidad', 0)) for compra in compras)
    
    total_kg_procesados = sum(float(proceso.get('kg_resultantes', 0)) for proceso in procesos)
    rendimiento_promedio = (total_kg_procesados / total_kg_comprados * 100) if total_kg_comprados > 0 else 0
    
    total_gastos = sum(float(gasto.get('monto', 0)) for gasto in gastos)
    
    total_ventas = sum(float(venta.get('total', 0)) for venta in ventas)
    total_kg_vendidos = sum(float(venta.get('cantidad', 0)) for venta in ventas)
    
    total_utilidad = sum(float(venta.get('utilidad', 0)) for venta in ventas) - total_gastos
    
    # Preparar mensaje
    mensaje = "📊 *REPORTE GENERAL*\n\n"
    
    mensaje += "*Compras:*\n"
    mensaje += f"Total: {format_currency(total_compras)}\n"
    mensaje += f"Café comprado: {total_kg_comprados:.2f}kg\n\n"
    
    mensaje += "*Procesamiento:*\n"
    mensaje += f"Café procesado: {total_kg_procesados:.2f}kg\n"
    mensaje += f"Rendimiento promedio: {rendimiento_promedio:.2f}%\n\n"
    
    mensaje += "*Gastos:*\n"
    mensaje += f"Total: {format_currency(total_gastos)}\n\n"
    
    mensaje += "*Ventas:*\n"
    mensaje += f"Total: {format_currency(total_ventas)}\n"
    mensaje += f"Café vendido: {total_kg_vendidos:.2f}kg\n\n"
    
    mensaje += "*Balance:*\n"
    mensaje += f"Utilidad: {format_currency(total_utilidad)}\n"
    
    # Enviar mensaje
    await update.message.reply_text(mensaje)

def _filtrar_por_periodo(datos, fecha_inicio, fecha_clave='fecha'):
    """Filtra datos por período"""
    return [
        dato for dato in datos 
        if dato.get(fecha_clave) and datetime.strptime(dato[fecha_clave], '%Y-%m-%d %H:%M:%S') >= fecha_inicio
    ]

async def reporte_diario(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Genera un reporte del día actual"""
    # Fecha de inicio (hoy a las 00:00)
    hoy = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Leer y filtrar datos
    compras = _filtrar_por_periodo(read_from_csv(COMPRAS_FILE), hoy)
    procesos = _filtrar_por_periodo(read_from_csv(PROCESO_FILE), hoy)
    gastos = _filtrar_por_periodo(read_from_csv(GASTOS_FILE), hoy)
    ventas = _filtrar_por_periodo(read_from_csv(VENTAS_FILE), hoy)
    
    if not compras and not procesos and not gastos and not ventas:
        await update.message.reply_text(
            "No hay operaciones registradas para hoy."
        )
        return
    
    # Calcular totales
    total_compras = sum(float(compra.get('total', 0)) for compra in compras)
    total_kg_comprados = sum(float(compra.get('cantidad', 0)) for compra in compras)
    
    total_kg_procesados = sum(float(proceso.get('kg_resultantes', 0)) for proceso in procesos)
    
    total_gastos = sum(float(gasto.get('monto', 0)) for gasto in gastos)
    
    total_ventas = sum(float(venta.get('total', 0)) for venta in ventas)
    total_kg_vendidos = sum(float(venta.get('cantidad', 0)) for venta in ventas)
    
    total_utilidad = sum(float(venta.get('utilidad', 0)) for venta in ventas) - total_gastos
    
    # Preparar mensaje
    mensaje = f"📊 *REPORTE DIARIO ({hoy.strftime('%d/%m/%Y')})*\n\n"
    
    mensaje += "*Compras:*\n"
    if compras:
        mensaje += f"Total: {format_currency(total_compras)}\n"
        mensaje += f"Café comprado: {total_kg_comprados:.2f}kg\n"
        for compra in compras:
            mensaje += f"- {compra['proveedor']}: {compra['cantidad']}kg a {format_currency(float(compra['precio_kg']))}/kg\n"
    else:
        mensaje += "No hubo compras hoy\n"
    mensaje += "\n"
    
    mensaje += "*Procesamiento:*\n"
    if procesos:
        mensaje += f"Café procesado: {total_kg_procesados:.2f}kg\n"
        for proceso in procesos:
            mensaje += f"- {proceso['tipo_proceso']}: {proceso['kg_resultantes']}kg ({proceso['rendimiento']}%)\n"
    else:
        mensaje += "No hubo procesamiento hoy\n"
    mensaje += "\n"
    
    mensaje += "*Gastos:*\n"
    if gastos:
        mensaje += f"Total: {format_currency(total_gastos)}\n"
        for gasto in gastos:
            mensaje += f"- {gasto['categoria']}: {format_currency(float(gasto['monto']))} ({gasto['descripcion']})\n"
    else:
        mensaje += "No hubo gastos hoy\n"
    mensaje += "\n"
    
    mensaje += "*Ventas:*\n"
    if ventas:
        mensaje += f"Total: {format_currency(total_ventas)}\n"
        mensaje += f"Café vendido: {total_kg_vendidos:.2f}kg\n"
        for venta in ventas:
            mensaje += f"- {venta['cliente']}: {venta['cantidad']}kg a {format_currency(float(venta['precio_kg']))}/kg\n"
    else:
        mensaje += "No hubo ventas hoy\n"
    mensaje += "\n"
    
    mensaje += "*Balance del día:*\n"
    mensaje += f"Utilidad: {format_currency(total_utilidad)}\n"
    
    # Enviar mensaje
    await update.message.reply_text(mensaje)

async def reporte_semanal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Genera un reporte de la semana actual"""
    # Fecha de inicio (hace 7 días a las 00:00)
    inicio_semana = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=7)
    
    # Leer y filtrar datos
    compras = _filtrar_por_periodo(read_from_csv(COMPRAS_FILE), inicio_semana)
    procesos = _filtrar_por_periodo(read_from_csv(PROCESO_FILE), inicio_semana)
    gastos = _filtrar_por_periodo(read_from_csv(GASTOS_FILE), inicio_semana)
    ventas = _filtrar_por_periodo(read_from_csv(VENTAS_FILE), inicio_semana)
    
    if not compras and not procesos and not gastos and not ventas:
        await update.message.reply_text(
            "No hay operaciones registradas en los últimos 7 días."
        )
        return
    
    # Calcular totales (similar al reporte diario pero para la semana)
    total_compras = sum(float(compra.get('total', 0)) for compra in compras)
    total_kg_comprados = sum(float(compra.get('cantidad', 0)) for compra in compras)
    
    total_kg_procesados = sum(float(proceso.get('kg_resultantes', 0)) for proceso in procesos)
    
    total_gastos = sum(float(gasto.get('monto', 0)) for gasto in gastos)
    gastos_por_categoria = {}
    for gasto in gastos:
        categoria = gasto.get('categoria', 'Otros')
        monto = float(gasto.get('monto', 0))
        if categoria in gastos_por_categoria:
            gastos_por_categoria[categoria] += monto
        else:
            gastos_por_categoria[categoria] = monto
    
    total_ventas = sum(float(venta.get('total', 0)) for venta in ventas)
    total_kg_vendidos = sum(float(venta.get('cantidad', 0)) for venta in ventas)
    
    total_utilidad = sum(float(venta.get('utilidad', 0)) for venta in ventas) - total_gastos
    
    # Preparar mensaje
    mensaje = f"📊 *REPORTE SEMANAL ({inicio_semana.strftime('%d/%m/%Y')} - {datetime.now().strftime('%d/%m/%Y')})*\n\n"
    
    mensaje += "*Compras:*\n"
    if compras:
        mensaje += f"Total: {format_currency(total_compras)}\n"
        mensaje += f"Café comprado: {total_kg_comprados:.2f}kg\n"
    else:
        mensaje += "No hubo compras esta semana\n"
    mensaje += "\n"
    
    mensaje += "*Procesamiento:*\n"
    if procesos:
        mensaje += f"Café procesado: {total_kg_procesados:.2f}kg\n"
    else:
        mensaje += "No hubo procesamiento esta semana\n"
    mensaje += "\n"
    
    mensaje += "*Gastos:*\n"
    if gastos:
        mensaje += f"Total: {format_currency(total_gastos)}\n"
        mensaje += "Por categoría:\n"
        for categoria, monto in gastos_por_categoria.items():
            mensaje += f"- {categoria}: {format_currency(monto)}\n"
    else:
        mensaje += "No hubo gastos esta semana\n"
    mensaje += "\n"
    
    mensaje += "*Ventas:*\n"
    if ventas:
        mensaje += f"Total: {format_currency(total_ventas)}\n"
        mensaje += f"Café vendido: {total_kg_vendidos:.2f}kg\n"
    else:
        mensaje += "No hubo ventas esta semana\n"
    mensaje += "\n"
    
    mensaje += "*Balance semanal:*\n"
    mensaje += f"Utilidad: {format_currency(total_utilidad)}\n"
    
    # Enviar mensaje
    await update.message.reply_text(mensaje)

async def reporte_mensual(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Genera un reporte del mes actual"""
    # Fecha de inicio (hace 30 días a las 00:00)
    inicio_mes = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=30)
    
    # Leer y filtrar datos
    compras = _filtrar_por_periodo(read_from_csv(COMPRAS_FILE), inicio_mes)
    procesos = _filtrar_por_periodo(read_from_csv(PROCESO_FILE), inicio_mes)
    gastos = _filtrar_por_periodo(read_from_csv(GASTOS_FILE), inicio_mes)
    ventas = _filtrar_por_periodo(read_from_csv(VENTAS_FILE), inicio_mes)
    
    if not compras and not procesos and not gastos and not ventas:
        await update.message.reply_text(
            "No hay operaciones registradas en los últimos 30 días."
        )
        return
    
    # Calcular totales (similar al reporte semanal pero para el mes)
    total_compras = sum(float(compra.get('total', 0)) for compra in compras)
    total_kg_comprados = sum(float(compra.get('cantidad', 0)) for compra in compras)
    
    total_kg_procesados = sum(float(proceso.get('kg_resultantes', 0)) for proceso in procesos)
    rendimiento_promedio = (total_kg_procesados / total_kg_comprados * 100) if total_kg_comprados > 0 else 0
    
    total_gastos = sum(float(gasto.get('monto', 0)) for gasto in gastos)
    gastos_por_categoria = {}
    for gasto in gastos:
        categoria = gasto.get('categoria', 'Otros')
        monto = float(gasto.get('monto', 0))
        if categoria in gastos_por_categoria:
            gastos_por_categoria[categoria] += monto
        else:
            gastos_por_categoria[categoria] = monto
    
    total_ventas = sum(float(venta.get('total', 0)) for venta in ventas)
    total_kg_vendidos = sum(float(venta.get('cantidad', 0)) for venta in ventas)
    margen_promedio = sum(float(venta.get('margen', 0)) for venta in ventas) / len(ventas) if ventas else 0
    
    total_utilidad = sum(float(venta.get('utilidad', 0)) for venta in ventas) - total_gastos
    
    # Preparar mensaje
    mensaje = f"📊 *REPORTE MENSUAL ({inicio_mes.strftime('%d/%m/%Y')} - {datetime.now().strftime('%d/%m/%Y')})*\n\n"
    
    mensaje += "*Compras:*\n"
    if compras:
        mensaje += f"Total: {format_currency(total_compras)}\n"
        mensaje += f"Café comprado: {total_kg_comprados:.2f}kg\n"
        mensaje += f"Precio promedio: {format_currency(total_compras/total_kg_comprados) if total_kg_comprados > 0 else 0}/kg\n"
    else:
        mensaje += "No hubo compras este mes\n"
    mensaje += "\n"
    
    mensaje += "*Procesamiento:*\n"
    if procesos:
        mensaje += f"Café procesado: {total_kg_procesados:.2f}kg\n"
        mensaje += f"Rendimiento promedio: {rendimiento_promedio:.2f}%\n"
    else:
        mensaje += "No hubo procesamiento este mes\n"
    mensaje += "\n"
    
    mensaje += "*Gastos:*\n"
    if gastos:
        mensaje += f"Total: {format_currency(total_gastos)}\n"
        mensaje += "Por categoría:\n"
        for categoria, monto in gastos_por_categoria.items():
            mensaje += f"- {categoria}: {format_currency(monto)}\n"
    else:
        mensaje += "No hubo gastos este mes\n"
    mensaje += "\n"
    
    mensaje += "*Ventas:*\n"
    if ventas:
        mensaje += f"Total: {format_currency(total_ventas)}\n"
        mensaje += f"Café vendido: {total_kg_vendidos:.2f}kg\n"
        mensaje += f"Precio promedio: {format_currency(total_ventas/total_kg_vendidos) if total_kg_vendidos > 0 else 0}/kg\n"
        mensaje += f"Margen promedio: {margen_promedio:.2f}%\n"
    else:
        mensaje += "No hubo ventas este mes\n"
    mensaje += "\n"
    
    mensaje += "*Balance mensual:*\n"
    mensaje += f"Utilidad: {format_currency(total_utilidad)}\n"
    
    # Enviar mensaje
    await update.message.reply_text(mensaje)

def register_reportes_handlers(application: Application):
    """Registra los handlers relacionados con reportes"""
    application.add_handler(CommandHandler("reporte", reporte_general))
    application.add_handler(CommandHandler("reporte_diario", reporte_diario))
    application.add_handler(CommandHandler("reporte_semanal", reporte_semanal))
    application.add_handler(CommandHandler("reporte_mensual", reporte_mensual))