import whisper
from moviepy import VideoFileClip, TextClip, CompositeVideoClip

model = whisper.load_model("base")  # Whisper base model

def add_subtitles(video_path, output_path):
    result = model.transcribe(video_path)
    video = VideoFileClip(video_path)
    clips = []
    for s in result["segments"]:
        txt = TextClip(
            s["text"], fontsize=48, color="white", stroke_color="black",
            stroke_width=2, method="caption", size=(900,None)
        ).set_start(s["start"]).set_duration(s["end"]-s["start"]).set_position(("center","bottom"))
        clips.append(txt)
    CompositeVideoClip([video]+clips).write_videofile(
        output_path, codec="libx264", audio_codec="aac", fps=30
    )
