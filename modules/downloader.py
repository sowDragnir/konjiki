import os
import random
import time

import yt_dlp
from yt_dlp.utils import DownloadError

from config import COOKIES_FILE, COOKIES_BROWSER
from modules.logger import logger


class _YDLLogger:
    """Silencia yt-dlp, solo propaga errores reales."""

    def debug(self, msg):
        pass

    def info(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        logger.error(f"[yt-dlp] {msg}")


def _base_opts() -> dict:
    """Opciones comunes de yt-dlp, incluyendo cookies si están configuradas."""
    opts: dict = {
        "quiet": True,
        "no_warnings": True,
        "logger": _YDLLogger(),
    }

    # Cookies — prioridad: archivo > navegador
    if COOKIES_FILE and os.path.exists(COOKIES_FILE):
        opts["cookiefile"] = COOKIES_FILE
        logger.info(f"[downloader] Usando cookies de archivo: {COOKIES_FILE}")
    elif COOKIES_BROWSER:
        opts["cookiesfrombrowser"] = (COOKIES_BROWSER,)
        logger.info(f"[downloader] Usando cookies del navegador: {COOKIES_BROWSER}")

    return opts


# Secuencia de player_client a probar ante un 403.
# YouTube sirve el video de forma diferente según el cliente.
_PLAYER_CLIENTS = [
    ["web"],          # intento por defecto
    ["ios"],          # cliente móvil iOS (menos restricciones)
    ["android"],      # cliente Android
    ["tv_embedded"],  # cliente TV (sin verificación de edad)
]


def get_random_video_url(channel_url: str, archive_path: str | None = None) -> str:
    """Lista los videos de un canal y devuelve uno al azar que no haya sido descargado.

    channel_url  : URL del canal (ej. https://www.youtube.com/@FaztTech/videos)
    archive_path : ruta al archivo de yt-dlp (una línea por video descargado)
    """
    opts = _base_opts()
    opts.update({
        "extract_flat": "in_playlist",
    })

    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(channel_url, download=False)

    entries = info.get("entries", []) if info else []
    if not entries:
        raise ValueError(f"[downloader] No se encontraron videos en el canal: {channel_url}")

    # Filtrar videos ya descargados
    already_downloaded: set[str] = set()
    if archive_path and os.path.exists(archive_path):
        with open(archive_path) as f:
            for line in f:
                parts = line.strip().split()
                if parts:
                    already_downloaded.add(parts[-1])  # formato: "youtube <id>"

    available = [e for e in entries if e.get("id") not in already_downloaded]

    if not available:
        logger.warning(
            f"[downloader] Todos los videos del canal ya fueron descargados. "
            f"Reutilizando lista completa: {channel_url}"
        )
        available = entries

    video = random.choice(available)
    video_url = f"https://www.youtube.com/watch?v={video['id']}"
    logger.info(f"[downloader] Video elegido: {video.get('title', video['id'])} — {video_url}")
    return video_url


def download(video_url: str, vid: str, folder: str, max_retries: int = 3,
             archive_path: str | None = None) -> str:
    """Descarga un video concreto de YouTube con reintentos ante 403 y rate-limit.

    Ante un 403, rota automáticamente por diferentes player_client de yt-dlp
    (web → ios → android → tv_embedded) antes de rendirse.
    """
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, f"{vid}.mp4")

    if archive_path:
        os.makedirs(os.path.dirname(archive_path) or ".", exist_ok=True)

    last_error = None

    for attempt, player_clients in enumerate(_PLAYER_CLIENTS, start=1):
        if attempt > max_retries:
            break

        opts = _base_opts()
        opts.update({
            "format": "bestvideo*[height<=1080]+bestaudio*/best",
            "outtmpl": path,
            "merge_output_format": "mp4",
            "extractor_args": {"youtube": {"player_client": player_clients}},
        })
        if archive_path:
            opts["download_archive"] = archive_path

        try:
            logger.info(
                f"[downloader] Intento {attempt}/{max_retries} "
                f"(player={player_clients}): {video_url}"
            )
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([video_url])
            logger.info(f"[downloader] Descarga OK: {vid}")
            return path

        except DownloadError as e:
            msg = str(e)
            last_error = e
            logger.error(f"[downloader] Error (player={player_clients}): {msg}")

            if "403" in msg or "Forbidden" in msg or "Requested format is not available" in msg:
                logger.warning(
                    f"[downloader] Fallo ({msg.split(':')[-1].strip()}) con player={player_clients}, "
                    f"probando siguiente cliente..."
                )
                continue  # rotar al siguiente player_client

            if "rate-limited" in msg or "try again later" in msg:
                sleep_s = 10 * attempt
                logger.warning(f"[downloader] Rate-limit. Esperando {sleep_s}s...")
                time.sleep(sleep_s)
                continue

            # Otro error — no tiene sentido reintentar
            break

        except Exception as e:
            last_error = e
            logger.exception("[downloader] Error inesperado durante la descarga")
            break

    raise last_error if last_error else RuntimeError("Fallo en la descarga por razón desconocida")
