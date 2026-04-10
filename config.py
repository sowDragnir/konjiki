import os
from dotenv import load_dotenv

load_dotenv()

# ─── Canales fuente ───────────────────────────────────────────────────────────
# Añade aquí todos los canales que quieras. El sistema elige uno al azar,
# luego elige un video al azar dentro de ese canal.
CHANNELS = [
    "https://www.youtube.com/@BubbaDOSpanish/videos",
    "https://www.youtube.com/@Chriskidsshow/videos",
    "https://www.youtube.com/@BabyBusES/videos",
    # Añade más canales aquí:
    # "https://www.youtube.com/@NombreCanal/videos",
]

# ─── Pipeline ─────────────────────────────────────────────────────────────────
MAX_RETRIES   = 3
CLIP_DURATION = 45       # segundos del clip final

# ─── Cookies YouTube descarga (necesario para evitar 403 Forbidden) ───────────
# Opción A — archivo de cookies exportado desde el navegador (formato Netscape).
COOKIES_FILE = ""        # ej. "/home/sow/youtube_cookies.txt"

# Opción B — leer cookies directamente del navegador instalado en el sistema.
# Valores posibles: "chrome", "firefox", "brave", "edge", "" (desactivado)
COOKIES_BROWSER = "chrome"

# ─── Credenciales (cargadas desde .env) ───────────────────────────────────────
# Las credenciales reales van en .env (nunca en este archivo).
# Copia .env.example → .env y rellena los valores.
YOUTUBE_CLIENT_ID     = os.getenv("YOUTUBE_CLIENT_ID", "")
YOUTUBE_CLIENT_SECRET = os.getenv("YOUTUBE_CLIENT_SECRET", "")
INSTAGRAM_USER        = os.getenv("INSTAGRAM_USER", "")
INSTAGRAM_PASSWORD    = os.getenv("INSTAGRAM_PASSWORD", "")

# ─── Anti-copyright ───────────────────────────────────────────────────────────
# Transformaciones que se aplican al clip antes de exportar.
FLIP_HORIZONTAL = True    # Espejo horizontal
SPEED_FACTOR    = 1.05    # 1.0 = sin cambio, 1.05 = 5% más rápido
COLOR_FACTOR    = 1.03    # 1.0 = sin cambio, 1.03 = brillo/saturación +3%

# ─── Rutas ────────────────────────────────────────────────────────────────────
RAW_DIR           = "downloads"
OUT_DIR           = "output"
DB_PATH           = "konjiki.db"
LOG_PATH          = "logs/konjiki.log"
DOWNLOAD_ARCHIVE  = "downloads/archive.txt"
YOUTUBE_TOKEN     = "youtube_token.json"    # generado por setup_youtube_auth.py
INSTAGRAM_SESSION = "instagram_session.json"
SESSION_PATH      = "konjiki_session"
