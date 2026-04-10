# ─── Canales fuente ───────────────────────────────────────────────────────────
# Añade aquí todos los canales que quieras. El sistema elige uno al azar,
# luego elige un video al azar dentro de ese canal.
CHANNELS = [
    "https://www.youtube.com/@BubbaDOSpanish/videos",
    "https://www.youtube.com/@Chriskidsshow/videos",
    "https://www.youtube.com/@BabyBusES/videos"
    # Añade más canales aquí:
    # "https://www.youtube.com/@NombreCanal/videos",
]

# ─── Pipeline ─────────────────────────────────────────────────────────────────
MAX_RETRIES    = 3
CLIP_DURATION  = 45       # segundos del clip final

# ─── Cookies YouTube descarga (necesario para evitar 403 Forbidden) ───────────
# Opción A — archivo de cookies exportado desde el navegador (formato Netscape).
COOKIES_FILE = ""          # ej. "/home/sow/youtube_cookies.txt"

# Opción B — leer cookies directamente del navegador instalado en el sistema.
# Valores posibles: "chrome", "firefox", "brave", "edge", "" (desactivado)
COOKIES_BROWSER = "chrome"

# ─── YouTube Data API v3 (subida) ─────────────────────────────────────────────
# 1. Ve a https://console.cloud.google.com/
# 2. Crea un proyecto → Habilita "YouTube Data API v3"
# 3. Credenciales → OAuth 2.0 → Tipo: Aplicación de escritorio
# 4. Copia el Client ID y Client Secret aquí abajo
# 5. Ejecuta: python setup_youtube_auth.py  (una sola vez)
#    → abre el navegador para aprobar, luego guarda youtube_token.json
YOUTUBE_CLIENT_ID     = ""
YOUTUBE_CLIENT_SECRET = ""
# Obtén el refresh token en https://developers.google.com/oauthplayground
# → engranaje → "Use your own OAuth credentials" → scope: youtube.upload
# → Authorize → Exchange code for tokens → copia refresh_token
YOUTUBE_REFRESH_TOKEN = ""   # pega aquí el refresh_token

# ─── Instagram (subida) ───────────────────────────────────────────────────────
# Cuenta de Instagram donde se subirán los Reels.
# La sesión se guarda en instagram_session.json después del primer login,
# así no se envían credenciales en cada ejecución.
INSTAGRAM_USER     = ""    # ej. "mi_usuario"
INSTAGRAM_PASSWORD = ""    # ej. "mi_contraseña"
INSTAGRAM_SESSION  = "instagram_session.json"   # guardado automáticamente

# ─── Anti-copyright ───────────────────────────────────────────────────────────
# Transformaciones que se aplican al clip antes de exportar.
# Cambian la huella digital del video para evitar Content ID.
FLIP_HORIZONTAL = True    # Espejo horizontal
SPEED_FACTOR    = 1.05    # 1.0 = sin cambio, 1.05 = 5% más rápido
COLOR_FACTOR    = 1.03    # 1.0 = sin cambio, 1.03 = brillo/saturación +3%

# ─── Rutas ────────────────────────────────────────────────────────────────────
RAW_DIR          = "downloads"
OUT_DIR          = "output"
DB_PATH          = "konjiki.db"
LOG_PATH         = "logs/konjiki.log"
DOWNLOAD_ARCHIVE = "downloads/archive.txt"   # Videos ya descargados (evita repetir)
