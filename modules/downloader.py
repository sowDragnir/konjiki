import os
import time

import yt_dlp
from yt_dlp.utils import DownloadError

from modules.logger import logger


class _YDLLogger:
    """Logger silencieux pour yt-dlp (on ne garde que les erreurs)."""

    def debug(self, msg):
        # Trop verbeux, on ignore
        pass

    def info(self, msg):
        # Tu peux décommenter si tu veux voir plus de détails yt-dlp
        # logger.info(f"[yt-dlp] {msg}")
        pass

    def warning(self, msg):
        # On cache les warnings bruyants de YouTube (JS runtime, SABR, etc.)
        pass

    def error(self, msg):
        logger.error(f"[yt-dlp] {msg}")


def download(CHANNELS, vid, folder, max_retries: int = 3):
    """Télécharge une vidéo et gère les erreurs / rate-limit de YouTube.

    CHANNELS : URL ou ID de vidéo (dans ton code: CHANNELS[0])
    vid      : identifiant local qu'on utilise pour le nom de fichier
    folder   : dossier de sortie
    """
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, f"{vid}.mp4")

    ydl_opts = {
        "format": "bestvideo[height<=1080]+bestaudio/best",
        "outtmpl": path,
        "merge_output_format": "mp4",
        "quiet": True,
        "no_warnings": True,
        "logger": _YDLLogger(),
        # Optionnel: archive pour éviter de retélécharger 1000x les mêmes vidéos
        # "download_archive": os.path.join(folder, "downloaded.txt"),
    }

    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(
                f"[downloader] Tentative {attempt}/{max_retries} de téléchargement: {CHANNELS}"
            )
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([CHANNELS])
            logger.info(f"[downloader] Téléchargement OK: {vid}")
            return path
        except DownloadError as e:
            msg = str(e)
            last_error = e
            logger.error(f"[downloader] Erreur yt_dlp: {msg}")

            # Cas fréquent : rate-limit / "try again later"
            if "rate-limited" in msg or "try again later" in msg:
                if attempt < max_retries:
                    sleep_s = 10 * attempt
                    logger.warning(
                        f"[downloader] Suspected rate-limit YouTube. Attente de {sleep_s}s avant nouvel essai..."
                    )
                    time.sleep(sleep_s)
                    continue
            # Pas de retry spécial -> on sort directement
            break
        except Exception as e:  # autre erreur imprévue
            last_error = e
            logger.exception("[downloader] Erreur inattendue pendant le téléchargement")
            break

    # Si on arrive ici, tous les essais ont échoué -> on propage pour que le job soit marqué FAILED
    raise last_error if last_error else RuntimeError("Échec du téléchargement pour une raison inconnue")
