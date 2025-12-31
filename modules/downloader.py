import yt_dlp
import os
from modules.logger import logger

def download(CHANNELS, vid, folder):
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, f"{vid}.mp4")
    ydl_opts = {
        "format": "bestvideo[height<=1080]+bestaudio/best",
        "outtmpl": path,
        "merge_output_format": "mp4",
        "quiet": True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([CHANNELS])
    logger.info(f"Descargado {vid}")
    return path
