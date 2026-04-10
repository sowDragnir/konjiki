import os
import tempfile

import librosa
import numpy as np
from moviepy import VideoFileClip

from modules.logger import logger


def detect_viral_segments(video_path: str, duration: float = 45) -> tuple[float, float]:
    """Detecta el segmento más interesante del video usando múltiples señales de audio.

    Combina:
      - Energía RMS media (volumen promedio de la ventana)
      - Densidad de onsets (ritmo / frecuencia de habla)
      - Varianza RMS (dinamismo: silencio → explosión de energía)

    Devuelve (start, end) en segundos.
    """
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            audio_path = os.path.join(tmpdir, "audio.wav")
            with VideoFileClip(video_path) as video:
                video_duration = video.duration
                if video.audio is None:
                    logger.warning("[viral_detector] El video no tiene audio, usando inicio.")
                    return 0.0, min(duration, video_duration)
                video.audio.write_audiofile(audio_path, logger=None)

            y, sr = librosa.load(audio_path, sr=None)

        # ── Señal 1: RMS (energía por frame) ──────────────────────────────────
        rms = librosa.feature.rms(y=y)[0].astype(float)
        times = librosa.frames_to_time(np.arange(len(rms)), sr=sr)

        # ── Señal 2: densidad de onsets ────────────────────────────────────────
        onset_frames = librosa.onset.onset_detect(y=y, sr=sr, units="frames")
        onset_density = np.zeros(len(rms))
        for of in onset_frames:
            if of < len(onset_density):
                onset_density[of] = 1.0

        # ── Ventana deslizante ─────────────────────────────────────────────────
        # Calcular cuántos frames de RMS equivalen a `duration` segundos
        hop_length = 512
        fps_rms = sr / hop_length
        window = max(1, int(duration * fps_rms))

        if window >= len(rms):
            # Video más corto que el clip deseado → devolver todo
            return 0.0, min(video_duration, duration)

        # Kernels de suma acumulada para deslizar en O(n)
        kernel = np.ones(window)

        rms_sum  = np.convolve(rms, kernel, mode="valid")           # energía total
        rms_sq   = np.convolve(rms ** 2, kernel, mode="valid")      # para varianza
        onset_sum = np.convolve(onset_density, kernel, mode="valid") # densidad onsets

        # Varianza ≈ E[x²] − E[x]²  (sin dividir por n, solo para ranking)
        rms_mean     = rms_sum / window
        rms_variance = (rms_sq / window) - rms_mean ** 2

        # ── Score combinado (pesos ajustables) ────────────────────────────────
        def _norm(arr: np.ndarray) -> np.ndarray:
            mn, mx = arr.min(), arr.max()
            return (arr - mn) / (mx - mn + 1e-9)

        score = (
            0.50 * _norm(rms_sum) +       # segmento con más energía
            0.30 * _norm(onset_sum) +     # más movimiento / habla
            0.20 * _norm(rms_variance)    # más dinamismo
        )

        best_idx   = int(score.argmax())
        start_time = float(times[min(best_idx, len(times) - 1)])
        start      = max(0.0, start_time)
        end        = min(start + duration, video_duration)

        logger.info(
            f"[viral_detector] Segmento detectado: {start:.2f}s — {end:.2f}s "
            f"(score={score[best_idx]:.3f})"
        )
        return start, end

    except Exception as e:
        logger.error(f"[viral_detector] Error: {e}")
        return 0.0, duration
