import csv
import os
import pandas as pd
from datetime import datetime
import logging
import platform

# Determinar si estamos en producción (Heroku)
IS_PRODUCTION = os.getenv('ENVIRONMENT', '').lower() == 'production'

# Si estamos en producción, importar el módulo de Excel
if IS_PRODUCTION:
    from utils.excel_db import excel_db

# Configuración de logging
logger = logging.getLogger(__name__)

def save_to_csv(file_path, data, fieldnames=None):
    """
    Guarda datos en un archivo CSV o Excel (en producción)
    
    Args:
        file_path (str): Ruta o nombre del archivo sin extensión
        data (dict): Diccionario con los datos a guardar
        fieldnames (list, optional): Lista de nombres de campos. Si es None, se usan las claves del diccionario.
    
    Returns:
        bool: True si se guardó correctamente, False en caso contrario
    """
    try:
        # Si estamos en producción, usar Excel
        if IS_PRODUCTION:
            # Extraer el nombre de la hoja del path
            sheet_name = os.path.basename(file_path).split('.')[0]
            return excel_db.append_data(sheet_name, data)
        
        # Modo desarrollo: usar CSV
        else:
            # Determinar si el archivo existe
            file_exists = os.path.exists(file_path)
            
            # Si no se especifican fieldnames, usar las claves del diccionario
            if fieldnames is None:
                fieldnames = list(data.keys())
            
            with open(file_path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                
                # Escribir encabezados si el archivo es nuevo
                if not file_exists:
                    writer.writeheader()
                
                # Escribir datos
                writer.writerow(data)
            
            return True
    except Exception as e:
        logger.error(f"Error al guardar en CSV/Excel: {e}")
        return False

def get_dataframe(file_path):
    """
    Lee un archivo CSV/Excel y lo devuelve como DataFrame de pandas
    
    Args:
        file_path (str): Ruta o nombre del archivo sin extensión
    
    Returns:
        DataFrame: DataFrame de pandas con los datos
    """
    try:
        # Si estamos en producción, usar Excel
        if IS_PRODUCTION:
            # Extraer el nombre de la hoja del path
            sheet_name = os.path.basename(file_path).split('.')[0]
            return excel_db.get_dataframe(sheet_name)
        
        # Modo desarrollo: usar CSV
        else:
            # Verificar si el archivo existe
            if not os.path.exists(file_path):
                # Si no existe, crear un DataFrame vacío
                return pd.DataFrame()
            
            # Leer CSV como DataFrame
            df = pd.read_csv(file_path)
            return df
    except Exception as e:
        logger.error(f"Error al leer CSV/Excel como DataFrame: {e}")
        return pd.DataFrame()

def read_from_csv(file_path):
    """
    Lee datos de un archivo CSV o Excel (en producción)
    
    Args:
        file_path (str): Ruta o nombre del archivo sin extensión
    
    Returns:
        list: Lista de diccionarios con los datos leídos
    """
    try:
        # Si estamos en producción, usar Excel
        if IS_PRODUCTION:
            # Extraer el nombre de la hoja del path
            sheet_name = os.path.basename(file_path).split('.')[0]
            df = excel_db.get_dataframe(sheet_name)
            return df.to_dict('records')
        
        # Modo desarrollo: usar CSV
        else:
            if not os.path.exists(file_path):
                return []
            
            with open(file_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                return list(reader)
    except Exception as e:
        logger.error(f"Error al leer CSV/Excel: {e}")
        return []

def update_csv(file_path, data_list, key_field='fecha'):
    """
    Actualiza un archivo CSV/Excel completo
    
    Args:
        file_path (str): Ruta o nombre del archivo sin extensión
        data_list (list): Lista de diccionarios con los datos a guardar
        key_field (str): Campo que se usa como clave para identificar registros
    
    Returns:
        bool: True si se actualizó correctamente, False en caso contrario
    """
    try:
        # Si no hay datos, no hacer nada
        if not data_list:
            return True
        
        # Si estamos en producción, usar Excel
        if IS_PRODUCTION:
            # Extraer el nombre de la hoja del path
            sheet_name = os.path.basename(file_path).split('.')[0]
            
            # Convertir la lista a DataFrame
            df = pd.DataFrame(data_list)
            
            # Guardar como una nueva hoja completa
            return excel_db._save_sheet(sheet_name, df)
        
        # Modo desarrollo: usar CSV
        else:
            # Obtener los nombres de campos del primer registro
            fieldnames = list(data_list[0].keys())
            
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data_list)
            
            return True
    except Exception as e:
        logger.error(f"Error al actualizar CSV/Excel: {e}")
        return False

def update_record(file_path, record_id, updates, id_field='fecha'):
    """
    Actualiza un solo registro en un archivo CSV o Excel (en producción)
    
    Args:
        file_path (str): Ruta o nombre del archivo sin extensión
        record_id (str): Valor del campo id_field para identificar el registro
        updates (dict): Diccionario con los campos a actualizar
        id_field (str): Campo que se usa como identificador
    
    Returns:
        bool: True si se actualizó correctamente, False en caso contrario
    """
    try:
        # Si estamos en producción, usar Excel
        if IS_PRODUCTION:
            # Extraer el nombre de la hoja del path
            sheet_name = os.path.basename(file_path).split('.')[0]
            return excel_db.update_data(sheet_name, id_field, record_id, updates)
        
        # Modo desarrollo: usar CSV
        else:
            # Leer todos los registros
            records = read_from_csv(file_path)
            
            # Actualizar el registro específico
            updated = False
            for record in records:
                if record[id_field] == record_id:
                    record.update(updates)
                    updated = True
            
            if not updated:
                return False
            
            # Escribir todos los registros de vuelta al archivo
            return update_csv(file_path, records, id_field)
    except Exception as e:
        logger.error(f"Error al actualizar registro: {e}")
        return False

def get_record_by_id(file_path, record_id, id_field='fecha'):
    """
    Obtiene un registro específico por su ID
    
    Args:
        file_path (str): Ruta o nombre del archivo sin extensión
        record_id (str): Valor del campo id_field para identificar el registro
        id_field (str): Campo que se usa como identificador
    
    Returns:
        dict: Registro encontrado o None si no existe
    """
    try:
        # Si estamos en producción, usar DataFrame
        if IS_PRODUCTION:
            # Extraer el nombre de la hoja del path
            sheet_name = os.path.basename(file_path).split('.')[0]
            df = excel_db.get_dataframe(sheet_name)
            if df.empty:
                return None
            
            # Filtrar por ID
            filtered = df[df[id_field] == record_id]
            if filtered.empty:
                return None
            
            # Devolver como diccionario
            return filtered.iloc[0].to_dict()
        
        # Modo desarrollo: usar CSV
        else:
            records = read_from_csv(file_path)
            for record in records:
                if record[id_field] == record_id:
                    return record
            return None
    except Exception as e:
        logger.error(f"Error al obtener registro por ID: {e}")
        return None