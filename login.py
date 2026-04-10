"""
Ejecuta este script UNA SOLA VEZ para iniciar sesión manualmente.
La sesión queda guardada en konjiki_session/ y konjiki.py la reutiliza
en todas las ejecuciones futuras sin volver a pedir credenciales.

Uso:
    .venv/bin/python login.py
"""
import os
import time
import undetected_chromedriver as uc
from config import SESSION_PATH

options = uc.ChromeOptions()
options.add_argument(f"--user-data-dir={os.path.abspath(SESSION_PATH)}")
options.add_argument("--profile-directory=Default")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")

print("Abriendo Chrome...")
driver = uc.Chrome(
    options=options,
    headless=False,
    use_subprocess=True,
    version_main=143
)

print("\n── PASO 1: YouTube ──────────────────────────────")
print("Inicia sesión en YouTube Studio con tu cuenta de Google.")
driver.get("https://studio.youtube.com/")
input("Cuando hayas iniciado sesión y veas el dashboard de YouTube Studio, pulsa ENTER aquí...")

print("\n── PASO 2: Instagram ────────────────────────────")
print("Inicia sesión en Instagram.")
driver.get("https://www.instagram.com/")
input("Cuando hayas iniciado sesión y veas el feed de Instagram, pulsa ENTER aquí...")

driver.quit()
print("\nSesión guardada en:", os.path.abspath(SESSION_PATH))
print("Ya puedes ejecutar konjiki.py normalmente.")
