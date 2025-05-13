from datetime import datetime
import locale
import os

# Intentar configurar el locale para formateo de moneda
try:
    # Configuración para español de Perú (para formateo de moneda)
    locale.setlocale(locale.LC_ALL, 'es_PE.UTF-8')
except:
    try:
        # Alternativa: español genérico
        locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')
    except:
        try:
            # Alternativa en Windows
            locale.setlocale(locale.LC_ALL, 'Spanish')
        except:
            # Si todo falla, usar configuración por defecto
            locale.setlocale(locale.LC_ALL, '')

def get_current_timestamp():
    """
    Obtiene la fecha y hora actual en formato YYYY-MM-DD HH:MM:SS
    
    Returns:
        str: Timestamp actual formateado
    """
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def get_current_date():
    """
    Obtiene la fecha actual en formato YYYY-MM-DD
    
    Returns:
        str: Fecha actual formateada
    """
    return datetime.now().strftime('%Y-%m-%d')

def get_current_time():
    """
    Obtiene la hora actual en formato HH:MM:SS
    
    Returns:
        str: Hora actual formateada
    """
    return datetime.now().strftime('%H:%M:%S')

def format_currency(amount):
    """
    Formatea un valor como moneda (Soles peruanos)
    
    Args:
        amount (float): Monto a formatear
    
    Returns:
        str: Monto formateado como moneda
    """
    try:
        return f"S/ {float(amount):.2f}"
    except:
        return f"S/ 0.00"

def calculate_total(quantity, price):
    """
    Calcula el total a partir de cantidad y precio
    
    Args:
        quantity (float): Cantidad
        price (float): Precio unitario
    
    Returns:
        float: Total calculado
    """
    try:
        return float(quantity) * float(price)
    except:
        return 0.0

def parse_float(value, default=0.0):
    """
    Convierte un valor a float de forma segura
    
    Args:
        value: Valor a convertir
        default (float, optional): Valor por defecto si la conversión falla
    
    Returns:
        float: Valor convertido o default
    """
    try:
        return float(value)
    except:
        return default

def calculate_percentage(part, total):
    """
    Calcula un porcentaje
    
    Args:
        part (float): Parte
        total (float): Total
    
    Returns:
        float: Porcentaje calculado
    """
    if float(total) == 0:
        return 0.0
    return (float(part) / float(total)) * 100.0

def format_date(date_str):
    """
    Formatea una fecha YYYY-MM-DD a DD/MM/YYYY
    
    Args:
        date_str (str): Fecha en formato YYYY-MM-DD
    
    Returns:
        str: Fecha formateada
    """
    try:
        date = datetime.strptime(date_str.split(' ')[0], '%Y-%m-%d')
        return date.strftime('%d/%m/%Y')
    except:
        return date_str

def date_to_string(date):
    """
    Convierte un objeto datetime a string YYYY-MM-DD
    
    Args:
        date (datetime): Objeto datetime
    
    Returns:
        str: Fecha formateada
    """
    return date.strftime('%Y-%m-%d')

def string_to_date(date_str):
    """
    Convierte un string YYYY-MM-DD a objeto datetime
    
    Args:
        date_str (str): Fecha en formato YYYY-MM-DD
    
    Returns:
        datetime: Objeto datetime
    """
    try:
        # Si tiene hora, extraer solo la fecha
        if ' ' in date_str:
            date_str = date_str.split(' ')[0]
        return datetime.strptime(date_str, '%Y-%m-%d')
    except:
        return datetime.now()

def get_username(update):
    """
    Obtiene el nombre de usuario que mejor identifica al usuario
    
    Args:
        update: Objeto Update de Telegram
    
    Returns:
        str: Nombre de usuario
    """
    user = update.effective_user
    if user.username:
        return user.username
    elif user.first_name:
        if user.last_name:
            return f"{user.first_name} {user.last_name}"
        return user.first_name
    else:
        return str(user.id)
        
def truncate_text(text, max_length=4000):
    """
    Trunca un texto si es demasiado largo para Telegram
    
    Args:
        text (str): Texto a truncar
        max_length (int, optional): Longitud máxima
    
    Returns:
        str: Texto truncado si es necesario
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - 100] + "...\n\n(Texto truncado por exceder el límite de caracteres)"