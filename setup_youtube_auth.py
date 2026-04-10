"""
Ejecuta este script UNA SOLA VEZ para autorizar el acceso a YouTube.

Pasos previos:
  1. Ve a https://console.cloud.google.com/
  2. Crea un proyecto → Activa "YouTube Data API v3"
  3. Credenciales → OAuth 2.0 → Aplicación de escritorio
  4. Copia el Client ID y Client Secret en config.py
  5. Ejecuta: .venv/bin/python setup_youtube_auth.py
     → Abre el navegador para que apruebes el acceso
     → Guarda youtube_token.json (refresh_token incluido)

Usos futuros: konjiki.py renueva el token automáticamente.
"""
import sys
from google_auth_oauthlib.flow import InstalledAppFlow
from config import YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_TOKEN

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

if not YOUTUBE_CLIENT_ID or not YOUTUBE_CLIENT_SECRET:
    print("ERROR: Rellena YOUTUBE_CLIENT_ID y YOUTUBE_CLIENT_SECRET en config.py")
    sys.exit(1)

client_config = {
    "installed": {
        "client_id":     YOUTUBE_CLIENT_ID,
        "client_secret": YOUTUBE_CLIENT_SECRET,
        "redirect_uris": ["http://localhost"],
        "auth_uri":      "https://accounts.google.com/o/oauth2/auth",
        "token_uri":     "https://oauth2.googleapis.com/token",
    }
}

print("Abriendo navegador para autorizar acceso a YouTube...")
flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
creds = flow.run_local_server(port=0)

with open(YOUTUBE_TOKEN, "w") as f:
    f.write(creds.to_json())

print(f"\nToken guardado en: {YOUTUBE_TOKEN}")
print("Ya puedes ejecutar konjiki.py — el token se renueva automáticamente.")
