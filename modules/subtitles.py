import shutil
import warnings

import whisper
from moviepy import VideoFileClip, TextClip, CompositeVideoClip

from modules.logger import logger

warnings.filterwarnings(
    "ignore",
    message="FP16 is not supported on CPU; using FP32 instead",
)

# Fuente del sistema — ruta completa requerida por moviepy 2
_FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

model = whisper.load_model("base")


def add_subtitles(video_path: str, output_path: str) -> None:
    """Transcribe el audio con Whisper y añade subtítulos al video.

    Si falla cualquier paso, copia el video sin subtítulos para no bloquear el job.
    """
    try:
        result = model.transcribe(video_path)
        video = VideoFileClip(video_path)
        clips = []

        for s in result["segments"]:
            txt = (
                TextClip(
                    font=_FONT,
                    text=s["text"].strip(),
                    font_size=50,
                    color="white",
                    stroke_color="black",
                    stroke_width=2,
                    method="caption",
                    size=(900, None),
                )
                .with_start(s["start"])
                .with_duration(s["end"] - s["start"])
                .with_position(("center", "bottom"))
            )
            clips.append(txt)

        final_clip = CompositeVideoClip([video] + clips)
        final_clip.write_videofile(
            output_path,
            codec="libx264",
            audio_codec="aac",
            fps=30,
            logger=None,
        )
        video.close()
        final_clip.close()
        logger.info("[subtitles] Subtítulos generados correctamente")

    except Exception:
        logger.exception("[subtitles] Error generando subtítulos — copiando video sin subtítulos")
        shutil.copy(video_path, output_path)
