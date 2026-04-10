import numpy as np
from moviepy import VideoFileClip

from config import CLIP_DURATION, FLIP_HORIZONTAL, SPEED_FACTOR, COLOR_FACTOR
from modules.viral_detector import detect_viral_segments
from modules.logger import logger


def _build_transform(flip: bool, color: float):
    """Devuelve una función de transformación de frame para anti-copyright.

    Se combina flip + ajuste de color en una sola pasada por frame
    para no degradar el rendimiento.
    """
    def transform(frame: np.ndarray) -> np.ndarray:
        if flip:
            frame = frame[:, ::-1]          # espejo horizontal
        if color != 1.0:
            frame = np.clip(frame.astype(np.float32) * color, 0, 255).astype(np.uint8)
        return frame
    return transform


def make_short(input_video: str, output_video: str) -> None:
    """Recorta el segmento más viral, lo convierte a 9:16 y aplica transformaciones
    anti-copyright (flip, velocidad, ajuste de color).
    """
    start, end = detect_viral_segments(input_video, duration=CLIP_DURATION)

    with VideoFileClip(input_video) as v:
        duration = v.duration

        # ── Validación de rango ────────────────────────────────────────────────
        start = max(0.0, start if start is not None else 0.0)
        end   = min(end   if end   is not None else duration, duration)
        if start >= end:
            logger.warning(f"[editor] Rango inválido ({start}s-{end}s), usando video completo.")
            start, end = 0.0, duration

        clip = v.subclipped(start, end)

        # ── Recorte a 9:16 centrado ────────────────────────────────────────────
        w, h = clip.size
        target_w = int(h * 9 / 16)
        if target_w > w:
            # Video ya más estrecho que 9:16 (poco común), adaptar altura
            target_w = w
        clip = clip.cropped(x_center=w / 2, width=target_w).resized(height=1080)

        # ── Anti-copyright: flip + color ───────────────────────────────────────
        transform = _build_transform(FLIP_HORIZONTAL, COLOR_FACTOR)
        clip = clip.image_transform(transform)

        # ── Anti-copyright: velocidad ──────────────────────────────────────────
        if SPEED_FACTOR != 1.0:
            clip = clip.with_speed_scaled(SPEED_FACTOR)
            logger.info(f"[editor] Velocidad ajustada x{SPEED_FACTOR}")

        logger.info(
            f"[editor] Exportando short: {start:.1f}s-{end:.1f}s "
            f"→ flip={FLIP_HORIZONTAL}, speed={SPEED_FACTOR}, color={COLOR_FACTOR}"
        )

        clip.write_videofile(
            output_video,
            codec="libx264",
            audio_codec="aac",
            fps=30,
            preset="fast",      # mejor calidad que ultrafast con poco coste extra
            threads=2,
            logger=None,
        )
