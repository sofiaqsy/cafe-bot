import logging
from telegram import Update
from telegram.ext import ContextTypes

# Configuración de logging
logger = logging.getLogger(__name__)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Maneja el comando /start"""
    nombre = update.effective_user.first_name
    await update.message.reply_text(
        f"¡Hola {nombre}! Bienvenido al Bot de Gestión de Café.\n\n"
        "Este bot te ayudará a gestionar operaciones relacionadas con tu negocio de café, "
        "desde la compra de café en cereza hasta la venta final.\n\n"
        "Usa /ayuda o /help para ver la lista de comandos disponibles."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Maneja el comando /help o /ayuda"""
    await update.message.reply_text(
        "🤖 *COMANDOS DISPONIBLES*\n\n"
        "*Compras:*\n"
        "/compra - Registrar compra de café\n"
        "/compras - Ver compras registradas\n\n"
        "*Procesamiento:*\n"
        "/proceso - Registrar procesamiento\n"
        "/procesos - Ver procesamientos registrados\n\n"
        "*Gastos:*\n"
        "/gasto - Registrar gasto\n"
        "/gastos - Ver gastos registrados\n\n"
        "*Ventas:*\n"
        "/venta - Registrar venta\n"
        "/ventas - Ver ventas registradas\n\n"
        "*Adelantos:*\n"
        "/adelanto - Registrar adelanto a proveedor\n"
        "/adelantos - Ver adelantos registrados\n"
        "/compra_adelanto - Compra usando adelanto previo\n\n"
        "*Pedidos:*\n"
        "/pedido - Registrar pedido\n"
        "/pedidos - Ver pedidos pendientes\n\n"
        "*Reportes:*\n"
        "/reporte - Reporte general\n"
        "/reporte_diario - Reporte del día\n"
        "/reporte_semanal - Reporte de la semana\n"
        "/reporte_mensual - Reporte del mes\n\n"
        "*Ayuda:*\n"
        "/help o /ayuda - Mostrar esta lista de comandos\n"
        "/cancelar - Cancelar operación en curso"
    )