import subprocess
import numpy as np
from moviepy import VideoFileClip
import cv2

from config import (
    CLIP_DURATION, FLIP_HORIZONTAL, SPEED_FACTOR, COLOR_FACTOR,
    BRIGHTNESS_FACTOR, CONTRAST_FACTOR, SATURATION_FACTOR,
    ROTATION_DEGREES, ZOOM_FACTOR, GAUSSIAN_NOISE_LEVEL,
    AUDIO_PITCH_SEMITONES, AUDIO_SPEED_FACTOR
)
from modules.viral_detector import detect_viral_segments
from modules.logger import logger


def _build_transform(flip: bool, color: float, brightness: float, contrast: float,
                     saturation: float, rotation: float, zoom: float, noise: float):
    """Devuelve una función de transformación de frame para anti-copyright.

    Combina múltiples transformaciones en una sola pasada:
    - Flip horizontal
    - Ajuste de color/brillo/contraste
    - Rotación ligera
    - Zoom
    - Ruido Gaussiano (dificulta el reconocimiento por Content ID)
    """
    def transform(frame: np.ndarray) -> np.ndarray:
        # 1. Espejo horizontal
        if flip:
            frame = frame[:, ::-1]

        # 2. Cambios de brillo, contraste, saturación
        frame = frame.astype(np.float32)
        
        # Brillo
        if brightness != 1.0:
            frame = frame * brightness
        
        # Contraste (alrededor del punto central 128)
        if contrast != 1.0:
            frame = 128 + (frame - 128) * contrast
        
        # Saturación (convertir a HSV, ajustar S, convertir de vuelta)
        if saturation != 1.0:
            frame_uint8 = np.clip(frame, 0, 255).astype(np.uint8)
            hsv = cv2.cvtColor(frame_uint8, cv2.COLOR_BGR2HSV).astype(np.float32)
            hsv[:, :, 1] = np.clip(hsv[:, :, 1] * saturation, 0, 255)
            frame = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR).astype(np.float32)
        
        # Color global
        if color != 1.0:
            frame = frame * color
        
        # 3. Rotación ligera
        if rotation != 0:
            h, w = frame.shape[:2]
            M = cv2.getRotationMatrix2D((w / 2, h / 2), rotation, 1.0)
            frame = cv2.warpAffine(frame.astype(np.uint8), M, (w, h)).astype(np.float32)
        
        # 4. Zoom (crop + resize)
        if zoom != 1.0 and zoom > 0:
            h, w = frame.shape[:2]
            new_w, new_h = int(w / zoom), int(h / zoom)
            x, y = (w - new_w) // 2, (h - new_h) // 2
            frame = frame[y:y+new_h, x:x+new_w]
            frame = cv2.resize(frame.astype(np.uint8), (w, h)).astype(np.float32)
        
        # 5. Ruido Gaussiano
        if noise > 0:
            gaussian_noise = np.random.normal(0, noise * 25.5, frame.shape)
            frame = frame + gaussian_noise
        
        # Clip y convert back
        frame = np.clip(frame, 0, 255).astype(np.uint8)
        return frame
    
    return transform


def _shift_audio_pitch(video_path: str, output_path: str, semitones: float, speed_factor: float = 1.0) -> bool:
    """Cambia el tono del audio en semitones y velocidad de audio usando ffmpeg.

    Parámetros:
    - semitones: cambio de tono (-12 a +12 típicamente)
    - speed_factor: velocidad del audio (1.0 = sin cambio, 1.1 = 10% más rápido)

    Devuelve True si tuvo éxito, False si ffmpeg no está disponible o falla.
    """
    if semitones == 0 and speed_factor == 1.0:
        return False
    
    # Calcular factor de pitch shift
    pitch_factor = 2 ** (semitones / 12)
    
    # ffmpeg audio filter complex:
    # 1. asetrate: cambia la frecuencia de muestreo (para cambiar el pitch sin cambiar la velocidad)
    # 2. aresample: resamplea de vuelta a 44100 Hz
    # 3. atempo: cambia la velocidad sin cambiar el pitch
    audio_filters = [f"asetrate=44100*{pitch_factor}"]
    audio_filters.append("aresample=44100")
    
    if speed_factor != 1.0:
        audio_filters.append(f"atempo={speed_factor}")
    
    audio_filter_str = ",".join(audio_filters)
    
    cmd = [
        "ffmpeg", "-y", "-i", video_path,
        "-vf", "null",
        "-af", audio_filter_str,
        "-c:v", "copy",
        output_path,
    ]
    result = subprocess.run(cmd, capture_output=True)
    return result.returncode == 0


def make_short(input_video: str, output_video: str) -> None:
    """Recorta el segmento más viral, lo convierte a 9:16 y aplica transformaciones
    anti-copyright agresivas (flip, velocidad, color, rotación, zoom, ruido, tono).
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

        # ── Recorte a 9:16 con zoom ligero (+2%) ──────────────────────────────
        w, h = clip.size
        target_w = int(h * 9 / 16)
        if target_w > w:
            target_w = w
        zoom = 1.02
        clip = clip.cropped(x_center=w / 2, width=target_w).resized(height=int(1080 * zoom)).cropped(y_center=int(1080 * zoom / 2), height=1080)

        # ── Anti-copyright: transformaciones complejas ──────────────────────────
        transform = _build_transform(
            flip=FLIP_HORIZONTAL,
            color=COLOR_FACTOR,
            brightness=BRIGHTNESS_FACTOR,
            contrast=CONTRAST_FACTOR,
            saturation=SATURATION_FACTOR,
            rotation=ROTATION_DEGREES,
            zoom=ZOOM_FACTOR,
            noise=GAUSSIAN_NOISE_LEVEL
        )
        clip = clip.image_transform(transform)

        # ── Anti-copyright: velocidad del video ────────────────────────────────
        if SPEED_FACTOR != 1.0:
            clip = clip.with_speed_scaled(SPEED_FACTOR)
            logger.info(f"[editor] Velocidad video ajustada x{SPEED_FACTOR}")

        logger.info(
            f"[editor] Exportando short: {start:.1f}s-{end:.1f}s "
            f"→ flip={FLIP_HORIZONTAL}, speed_video={SPEED_FACTOR}, "
            f"color={COLOR_FACTOR}, brightness={BRIGHTNESS_FACTOR}, "
            f"contrast={CONTRAST_FACTOR}, saturation={SATURATION_FACTOR}, "
            f"rotation={ROTATION_DEGREES}°, zoom={ZOOM_FACTOR}, "
            f"noise={GAUSSIAN_NOISE_LEVEL}, pitch={AUDIO_PITCH_SEMITONES:+}st, speed_audio={AUDIO_SPEED_FACTOR}"
        )

        clip.write_videofile(
            output_video,
            codec="libx264",
            audio_codec="aac",
            fps=30,
            preset="medium",
            bitrate="8000k",
            audio_bitrate="192k",
            threads=2,
            logger=None,
        )

        # ── Anti-copyright: tono y velocidad de audio ──────────────────────────
        if AUDIO_PITCH_SEMITONES != 0 or AUDIO_SPEED_FACTOR != 1.0:
            pitched = output_video.replace(".mp4", "_pitched.mp4")
            if _shift_audio_pitch(output_video, pitched, AUDIO_PITCH_SEMITONES, AUDIO_SPEED_FACTOR):
                import os
                os.replace(pitched, output_video)
                logger.info(
                    f"[editor] Audio ajustado: {AUDIO_PITCH_SEMITONES:+} semitones, "
                    f"velocidad x{AUDIO_SPEED_FACTOR}"
                )
