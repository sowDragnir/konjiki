import os

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
import google.auth.transport.requests

from instagrapi import Client as IGClient
from instagrapi.exceptions import LoginRequired, ChallengeRequired

from config import (
    YOUTUBE_TOKEN,
    INSTAGRAM_USER, INSTAGRAM_PASSWORD, INSTAGRAM_SESSION,
)
from modules.logger import logger


# ─── YouTube ──────────────────────────────────────────────────────────────────
def _get_youtube_service():
    """Devuelve un servicio autenticado cargando el token guardado por setup_youtube_auth.py.

    No abre navegador. El access token se renueva automáticamente via HTTP
    cuando caduca (cada ~1 hora).
    """
    if not os.path.exists(YOUTUBE_TOKEN):
        raise ValueError(
            f"No se encontró {YOUTUBE_TOKEN}. "
            "Ejecuta: python setup_youtube_auth.py"
        )

    creds = Credentials.from_authorized_user_file(YOUTUBE_TOKEN)
    if not creds.valid:
        creds.refresh(google.auth.transport.requests.Request())
    return build("youtube", "v3", credentials=creds)


def upload_youtube_short(video_path: str, title: str) -> bool:
    """Sube un video como YouTube Short usando la API oficial."""
    try:
        logger.info("[uploader] YouTube: iniciando subida via API...")
        youtube = _get_youtube_service()

        body = {
            "snippet": {
                "title": f"{title} #shorts",
                "description": "#shorts",
                "tags": ["shorts"],
                "categoryId": "22",    # People & Blogs
            },
            "status": {
                "privacyStatus": "public",
                "selfDeclaredMadeForKids": False,
            },
        }

        media = MediaFileUpload(
            video_path,
            mimetype="video/mp4",
            resumable=True,
            chunksize=4 * 1024 * 1024,   # 4 MB por chunk
        )

        request = youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media,
        )

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                pct = int(status.progress() * 100)
                logger.info("[uploader] YouTube: subiendo... %d%%", pct)

        video_id = response.get("id", "?")
        logger.info("[uploader] YouTube: subida completada — https://youtu.be/%s", video_id)
        return True

    except HttpError as e:
        logger.error("[uploader] YouTube: HttpError %d — %s", e.resp.status, e.content)
        return False
    except Exception as e:
        logger.error("[uploader] YouTube: error — %s", e)
        return False


# ─── Instagram ────────────────────────────────────────────────────────────────
def _get_instagram_client() -> IGClient:
    """Devuelve un cliente de Instagram autenticado.

    Intenta cargar la sesión guardada. Si no existe o es inválida,
    hace login con usuario/contraseña y guarda la sesión nueva.
    """
    if not INSTAGRAM_USER or not INSTAGRAM_PASSWORD:
        raise ValueError(
            "Configura INSTAGRAM_USER e INSTAGRAM_PASSWORD en config.py"
        )

    cl = IGClient()

    # Intentar sesión guardada
    if os.path.exists(INSTAGRAM_SESSION):
        try:
            cl.load_settings(INSTAGRAM_SESSION)
            cl.login(INSTAGRAM_USER, INSTAGRAM_PASSWORD)
            logger.info("[uploader] Instagram: sesión cargada desde %s", INSTAGRAM_SESSION)
            return cl
        except LoginRequired:
            logger.warning("[uploader] Instagram: sesión expirada, haciendo login nuevo...")
            cl = IGClient()

    # Login fresco
    cl.login(INSTAGRAM_USER, INSTAGRAM_PASSWORD)
    cl.dump_settings(INSTAGRAM_SESSION)
    logger.info("[uploader] Instagram: login OK, sesión guardada en %s", INSTAGRAM_SESSION)
    return cl


def upload_instagram_reel(video_path: str, caption: str) -> bool:
    """Sube un video como Instagram Reel."""
    try:
        logger.info("[uploader] Instagram: iniciando subida...")
        cl = _get_instagram_client()
        media = cl.clip_upload(video_path, caption=caption)
        logger.info("[uploader] Instagram: subida completada — media_id=%s", media.pk)
        return True

    except (LoginRequired, ChallengeRequired) as e:
        logger.error(
            "[uploader] Instagram: problema de autenticación — %s. "
            "Elimina %s y vuelve a ejecutar para hacer login nuevo.",
            e, INSTAGRAM_SESSION,
        )
        return False
    except Exception as e:
        logger.error("[uploader] Instagram: error — %s", e)
        return False


# ─── Master ───────────────────────────────────────────────────────────────────
def upload_all(video_path: str, title: str = "Konjiki Clip") -> None:
    """Sube a todas las plataformas. Cada una falla de forma independiente."""
    results = {
        "youtube":   upload_youtube_short(video_path, title),
        "instagram": upload_instagram_reel(video_path, f"{title} #reels #shorts"),
    }

    ok  = [p for p, r in results.items() if r]
    err = [p for p, r in results.items() if not r]
    if ok:
        logger.info("[uploader] OK: %s", ", ".join(ok))
    if err:
        logger.warning("[uploader] Fallidos: %s", ", ".join(err))
    if err and not ok:
        raise RuntimeError(f"Todas las subidas fallaron: {', '.join(err)}")
