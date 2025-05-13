import os
from dotenv import load_dotenv

# Cargar variables de entorno desde archivo .env (si existe)
load_dotenv()

# Token del bot (reemplaza esto con tu token real)
TOKEN = os.getenv("BOT_TOKEN", "7854205776:AAEKtv-sCct4SLVqmCGsVI-eke0Ff47QRGA")

# IDs de usuarios autorizados (opcional, para control de acceso)
AUTHORIZED_USERS = [
    # Lista de IDs de usuarios de Telegram que pueden usar el bot
    # Ejemplo: 123456789, 987654321
]

# Directorios de datos
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
COMPRAS_FILE = os.path.join(DATA_DIR, "compras.csv")
PROCESO_FILE = os.path.join(DATA_DIR, "proceso.csv")
GASTOS_FILE = os.path.join(DATA_DIR, "gastos.csv")
VENTAS_FILE = os.path.join(DATA_DIR, "ventas.csv")
PROCESO_COMPRAS_FILE = os.path.join(DATA_DIR, "proceso_compras.csv")
PEDIDOS_FILE = os.path.join(DATA_DIR, "pedidos.csv")
PEDIDOS_WHATSAPP_FILE = os.path.join(DATA_DIR, "pedidos_whatsapp.csv")
ADELANTOS_FILE = os.path.join(DATA_DIR, "adelantos.csv")

# Asegurarse de que el directorio de datos exista
os.makedirs(DATA_DIR, exist_ok=True)

# Estados de compras
ESTADO_PENDIENTE = "Pendiente"
ESTADO_PROCESADO_PARCIAL = "Procesado parcialmente"
ESTADO_PROCESADO_COMPLETO = "Procesado completamente"