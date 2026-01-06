import shutil
import warnings

import whisper
from moviepy import VideoFileClip, TextClip, CompositeVideoClip
from whisper import load_model

from modules.logger import logger

# Évite le warning bruyant de Whisper sur FP16/FP32 sur CPU
warnings.filterwarnings(
    "ignore",
    message="FP16 is not supported on CPU; using FP32 instead",
)

model = load_model("base")  # Whisper base model


def add_subtitles(video_path, output_path):
    """Ajoute des sous-titres avec Whisper.

    En cas d'erreur, on log et on copie simplement la vidéo originale
    vers output_path pour que le job ne soit pas bloqué.
    """
    try:
        result = model.transcribe(video_path)
        video = VideoFileClip(video_path)
        clips = []
        for s in result["segments"]:
            txt = (
                TextClip(
                    s["text"],
                    color="white",
                    stroke_color="black",
                    stroke_width=2,
                    method="caption",
                    size=(900, None),
                )
                .set_start(s["start"])
                .set_duration(s["end"] - s["start"])
                .set_position(("center", "bottom"))
            )
            clips.append(txt)

        final_clip = CompositeVideoClip([video] + clips)
        final_clip.write_videofile(
            output_path,
            codec="libx264",
            audio_codec="aac",
            fps=30,
            verbose=False,
            logger=None,
        )
        video.close()
        final_clip.close()
        logger.info("[subtitles] Sous-titres générés avec succès")
    except Exception:
        logger.exception(
            "[subtitles] Erreur lors de la génération des sous-titres, utilisation de la vidéo sans sous-titres"
        )
        shutil.copy(video_path, output_path)
