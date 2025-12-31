from moviepy import VideoFileClip
from modules.viral_detector import detect_viral_segments
from modules.logger import logger

def make_short(input_video, output_video):
    start, end = detect_viral_segments(input_video)
    
    with VideoFileClip(input_video) as v:
        duration = v.duration
        
        # Validación
        if start is None or end is None:
            logger.warning(f"Invalid segments: start={start}, end={end}. Using full video.")
            start, end = 0, duration
        
        start = max(0, start)
        end = min(end, duration)
        
        if start >= end:
            logger.warning(f"Invalid range: start={start}, end={end}. Using full video.")
            start, end = 0, duration
        
        clip = v.subclipped(start, end)
        w, h = clip.size
        clip = clip.cropped(x_center=w/2, width=h*9/16).resized(height=1080)
        clip.write_videofile(
            output_video, codec="libx264", audio_codec="aac", fps=30, threads=2, preset="ultrafast"
        )