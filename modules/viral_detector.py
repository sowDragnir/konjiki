import librosa
import numpy as np
from moviepy import VideoFileClip
from modules.logger import logger
import tempfile
import os

def detect_viral_segments(video_path, duration=45):
    try:
        # Extraer audio del video temporalmente
        with tempfile.TemporaryDirectory() as tmpdir:
            audio_path = os.path.join(tmpdir, "temp_audio.wav")
            with VideoFileClip(video_path) as video:
                video.audio.write_audiofile(audio_path)
            
            # Analizar audio
            y, sr = librosa.load(audio_path, sr=None)
            rms = librosa.feature.rms(y=y)[0]
            times = librosa.frames_to_time(np.arange(len(rms)), sr=sr)
            smooth = np.convolve(rms, np.ones(20)/20, mode="same")
            peak_index = smooth.argmax()
            peak_time = times[peak_index]
            start = max(0, peak_time - duration/2)
            end = start + duration
            logger.info(f"Detected viral segment: {start:.2f}s - {end:.2f}s")
            return start, end
    except Exception as e:
        logger.error(f"Error detecting viral segments: {e}")
        return 0, duration