import logging
from datetime import datetime
from telegram import Update
from telegram.ext import (
    ContextTypes, CommandHandler, ConversationHandler, 
    MessageHandler, filters, Application
)

from config import COMPRAS_FILE, ESTADO_PENDIENTE, ADELANTOS_FILE
from utils.validators import validate_number
from utils.db import save_to_csv, get_dataframe
from utils.helpers import get_current_timestamp, calculate_total, format_currency
import pandas as pd

# Estados para la conversación
PROVEEDOR, CANTIDAD, PRECIO, CALIDAD = range(4)

# Logger
logger = logging.getLogger(__name__)

async def iniciar_compra(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Inicia el proceso de registro de compra"""
    await update.message.reply_text(
        "¡Vamos a registrar una nueva compra de café!\n"
        "Por favor, dime el nombre del proveedor:"
    )
    return PROVEEDOR

async def guardar_proveedor(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Guarda el proveedor y pide la cantidad"""
    context.user_data["proveedor"] = update.message.text
    await update.message.reply_text(
        f"Proveedor: {context.user_data['proveedor']}\n"
        "Ahora, ¿cuántos kilogramos de café estás comprando?"
    )
    return CANTIDAD

async def guardar_cantidad(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Guarda la cantidad y pide el precio"""
    cantidad_text = update.message.text
    
    # Validar que sea un número válido
    if not validate_number(cantidad_text):
        await update.message.reply_text(
            "Por favor, ingresa un número válido para la cantidad."
        )
        return CANTIDAD
    
    cantidad = float(cantidad_text)
    context.user_data["cantidad"] = cantidad
    
    await update.message.reply_text(
        f"Cantidad: {context.user_data['cantidad']} kg\n"
        "¿Cuál es el precio por kilogramo?"
    )
    return PRECIO

async def guardar_precio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Guarda el precio y pide la calidad"""
    precio_text = update.message.text
    
    # Validar que sea un número válido
    if not validate_number(precio_text):
        await update.message.reply_text(
            "Por favor, ingresa un número válido para el precio."
        )
        return PRECIO
    
    precio = float(precio_text)
    context.user_data["precio"] = precio
    
    await update.message.reply_text(
        f"Precio: {format_currency(context.user_data['precio'])} por kg\n"
        "¿Cuál es la calidad del café? (Grado 1, Grado 2, etc.)"
    )
    return CALIDAD

async def guardar_calidad(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Guarda la calidad y finaliza el registro"""
    context.user_data["calidad"] = update.message.text
    
    # Calcular precio total
    cantidad = context.user_data["cantidad"]
    precio = context.user_data["precio"]
    total = calculate_total(cantidad, precio)
    
    # Verificar si el proveedor tiene adelantos disponibles
    try:
        df_adelantos = get_dataframe(ADELANTOS_FILE)
        proveedor = context.user_data["proveedor"]
        
        adelantos_proveedor = df_adelantos[df_adelantos['proveedor'] == proveedor]
        adelantos_proveedor = adelantos_proveedor[adelantos_proveedor['saldo_restante'] > 0]
        
        if not adelantos_proveedor.empty:
            # Hay adelantos disponibles
            total_adelantos = adelantos_proveedor['saldo_restante'].sum()
            
            await update.message.reply_text(
                f"⚠️ AVISO: El proveedor {proveedor} tiene adelantos por S/ {total_adelantos:.2f}\n\n"
                f"Para usar estos adelantos en esta compra, cancela y usa el comando /compra_adelanto"
            )
    except Exception as e:
        logger.error(f"Error verificando adelantos: {e}")
    
    # Preparar datos para guardar
    data = {
        "fecha": get_current_timestamp(),
        "proveedor": context.user_data["proveedor"],
        "cantidad": cantidad,
        "precio_kg": precio,
        "calidad": context.user_data["calidad"],
        "total": total,
        "usuario": update.effective_user.username or update.effective_user.first_name,
        "kg_disponibles": cantidad,  # Inicialmente, todo está disponible
        "estado": ESTADO_PENDIENTE    # Estado inicial: Pendiente
    }
    
    # Guardar en CSV
    if save_to_csv(COMPRAS_FILE, data):
        await update.message.reply_text(
            "✅ Compra registrada correctamente:\n\n"
            f"Proveedor: {context.user_data['proveedor']}\n"
            f"Cantidad: {context.user_data['cantidad']} kg\n"
            f"Precio por kg: {format_currency(context.user_data['precio'])}\n"
            f"Calidad: {context.user_data['calidad']}\n"
            f"Total a pagar: {format_currency(total)}\n"
            f"Estado: {ESTADO_PENDIENTE}"
        )
    else:
        await update.message.reply_text(
            "❌ Error al registrar la compra. Por favor, intenta nuevamente."
        )
    
    # Limpiar datos de usuario
    context.user_data.clear()
    return ConversationHandler.END

async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancela la conversación"""
    await update.message.reply_text(
        "Operación cancelada."
    )
    context.user_data.clear()
    return ConversationHandler.END

def register_compras_handlers(application: Application):
    """Registra los handlers relacionados con compras"""
    # Conversación para registrar compras
    compra_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('compra', iniciar_compra)],
        states={
            PROVEEDOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, guardar_proveedor)],
            CANTIDAD: [MessageHandler(filters.TEXT & ~filters.COMMAND, guardar_cantidad)],
            PRECIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, guardar_precio)],
            CALIDAD: [MessageHandler(filters.TEXT & ~filters.COMMAND, guardar_calidad)],
        },
        fallbacks=[CommandHandler('cancelar', cancelar)],
    )
    application.add_handler(compra_conv_handler)