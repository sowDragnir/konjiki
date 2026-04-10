import os
import random
import time

from config import CHANNELS, RAW_DIR, OUT_DIR, DOWNLOAD_ARCHIVE
from jobs.queue import init_db, add_job, mark_done, mark_failed
from modules.downloader import get_random_video_url, download
from modules.editor import make_short
from modules.subtitles import add_subtitles
from modules.uploader import upload_all
from modules.logger import logger

os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs("logs", exist_ok=True)


def _cleanup(*paths: str) -> None:
    """Elimina archivos intermedios silenciosamente."""
    for p in paths:
        try:
            if p and os.path.exists(p):
                os.remove(p)
        except Exception:
            pass


def job() -> None:
    conn = init_db()
    vid  = str(int(time.time()))
    add_job(conn, vid)

    raw   = None
    short = f"{OUT_DIR}/{vid}_short.mp4"
    final = f"{OUT_DIR}/{vid}_final.mp4"

    try:
        # 1. Elegir canal y video al azar
        if not CHANNELS:
            raise ValueError("La lista CHANNELS está vacía. Añade canales en config.py.")
        channel = random.choice(CHANNELS)
        logger.info(f"Canal elegido: {channel}")

        video_url = get_random_video_url(channel, archive_path=DOWNLOAD_ARCHIVE)

        # 2. Descargar
        raw = download(video_url, vid, RAW_DIR, archive_path=DOWNLOAD_ARCHIVE)

        # 3. Cortar + transformaciones anti-copyright
        make_short(raw, short)

        # 4. Subtítulos
        add_subtitles(short, final)

        # 5. Subir
        upload_all(final)

        mark_done(conn, vid)
        logger.info("JOB OK")

    except Exception:
        logger.exception("JOB ERROR")
        mark_failed(conn, vid)

    finally:
        _cleanup(raw, short)   # raw y short siempre se borran
        # final se borra solo si el job fue exitoso (ya subido)
        if os.path.exists(final) and not os.path.exists(short):
            _cleanup(final)
        conn.close()


job()
