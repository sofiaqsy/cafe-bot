import re
from datetime import datetime

def validate_number(text):
    """
    Valida si un texto es un número (entero o decimal)
    
    Args:
        text (str): Texto a validar
    
    Returns:
        bool: True si es un número válido, False en caso contrario
    """
    try:
        # Eliminar espacios y reemplazar comas por puntos
        text = text.strip().replace(',', '.')
        float(text)
        return True
    except:
        return False

def validate_phone(text):
    """
    Valida si un texto es un número de teléfono peruano
    
    Args:
        text (str): Texto a validar
    
    Returns:
        bool: True si es un teléfono válido, False en caso contrario
    """
    try:
        # Eliminar espacios y guiones
        text = re.sub(r'[\s-]', '', text)
        
        # Validar que sea un número de 9 dígitos que comience con 9
        if re.match(r'^9\d{8}$', text):
            return True
        
        # O un número fijo con código de área (01, 04, etc.)
        if re.match(r'^0\d{1,2}\d{6,7}$', text):
            return True
        
        return False
    except:
        return False

def validate_date(text):
    """
    Valida si un texto es una fecha válida en formato DD/MM/YYYY
    
    Args:
        text (str): Texto a validar
    
    Returns:
        bool: True si es una fecha válida, False en caso contrario
    """
    try:
        datetime.strptime(text, '%d/%m/%Y')
        return True
    except:
        return False

def validate_iso_date(text):
    """
    Valida si un texto es una fecha válida en formato YYYY-MM-DD
    
    Args:
        text (str): Texto a validar
    
    Returns:
        bool: True si es una fecha válida, False en caso contrario
    """
    try:
        datetime.strptime(text, '%Y-%m-%d')
        return True
    except:
        return False

def validate_email(text):
    """
    Valida si un texto es un correo electrónico válido
    
    Args:
        text (str): Texto a validar
    
    Returns:
        bool: True si es un correo válido, False en caso contrario
    """
    try:
        pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return re.match(pattern, text) is not None
    except:
        return False

def validate_text_length(text, min_length=1, max_length=None):
    """
    Valida si la longitud de un texto está dentro de los límites
    
    Args:
        text (str): Texto a validar
        min_length (int, optional): Longitud mínima
        max_length (int, optional): Longitud máxima
    
    Returns:
        bool: True si la longitud es válida, False en caso contrario
    """
    try:
        if len(text) < min_length:
            return False
        if max_length is not None and len(text) > max_length:
            return False
        return True
    except:
        return False

def validate_positive_number(text):
    """
    Valida si un texto es un número positivo
    
    Args:
        text (str): Texto a validar
    
    Returns:
        bool: True si es un número positivo, False en caso contrario
    """
    try:
        value = float(text.strip().replace(',', '.'))
        return value > 0
    except:
        return False

def validate_percentage(text):
    """
    Valida si un texto es un porcentaje válido (0-100)
    
    Args:
        text (str): Texto a validar
    
    Returns:
        bool: True si es un porcentaje válido, False en caso contrario
    """
    try:
        value = float(text.strip().replace(',', '.').replace('%', ''))
        return 0 <= value <= 100
    except:
        return False

def validate_not_empty(text):
    """
    Valida si un texto no está vacío
    
    Args:
        text (str): Texto a validar
    
    Returns:
        bool: True si no está vacío, False en caso contrario
    """
    return text.strip() != ''

def sanitize_text(text):
    """
    Sanitiza un texto para evitar problemas de caracteres especiales o inyección SQL
    
    Args:
        text (str): Texto a sanitizar
    
    Returns:
        str: Texto sanitizado
    """
    # Eliminar caracteres potencialmente peligrosos
    text = re.sub(r'[\'";]', '', text)
    
    # Limitar a longitud razonable
    text = text[:500]
    
    return text.strip()