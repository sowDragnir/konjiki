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
FLIP_HORIZONTAL        = True    # Espejo horizontal (reversible)
SPEED_FACTOR           = 1.08    # 1.0 = sin cambio, 1.08 = 8% más rápido (más agresivo)
COLOR_FACTOR           = 1.08    # 1.0 = sin cambio, 1.08 = brillo/saturación +8%
BRIGHTNESS_FACTOR      = 1.05    # Ajuste de brillo adicional (1.0 = sin cambio)
CONTRAST_FACTOR        = 1.06    # Ajuste de contraste (1.0 = sin cambio)
SATURATION_FACTOR      = 0.95    # Saturación (1.0 = original, <1 = desaturado, >1 = más saturado)
ROTATION_DEGREES       = 0.5     # Rotación ligera del video en grados (0 = desactivado)
ZOOM_FACTOR            = 1.02    # Zoom ligero (1.0 = sin cambio, 1.02 = +2%)
GAUSSIAN_NOISE_LEVEL   = 0.8     # Ruido Gaussiano (0 = desactivado, rango 0-2)
AUDIO_PITCH_SEMITONES  = 2.5     # Semitones a subir el tono (0 = desactivado, más agresivo)
AUDIO_SPEED_FACTOR     = 1.06    # Velocidad del audio independiente (1.0 = sin cambio)

# ─── Rutas ────────────────────────────────────────────────────────────────────
RAW_DIR           = "downloads"
OUT_DIR           = "output"
DB_PATH           = "konjiki.db"
LOG_PATH          = "logs/konjiki.log"
DOWNLOAD_ARCHIVE  = "downloads/archive.txt"
YOUTUBE_TOKEN     = "youtube_token.json"    # generado por setup_youtube_auth.py
INSTAGRAM_SESSION = "instagram_session.json"
SESSION_PATH      = "konjiki_session"
