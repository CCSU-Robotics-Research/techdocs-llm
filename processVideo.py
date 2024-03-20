import os
import ffmpeg
from datetime import datetime

def process_video(input_video_path):
    # Get the base filename of the input video
    base_filename = os.path.splitext(os.path.basename(input_video_path))[0]

    # Create a directory for the processed files
    output_directory = os.path.join("temp", f"{base_filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    os.makedirs(output_directory, exist_ok=True)

    # Transcode audio to CD quality .mp3
    audio_output_path = os.path.join(output_directory, f"{base_filename}_audio.mp3")
    (
        ffmpeg
        .input(input_video_path)
        .output(audio_output_path, ar=44100, ac=2, ab="192k")
        .run()
    )

    # Transcode video to 1080p 30fps @ 5kbit
    video_output_path = os.path.join(output_directory, f"{base_filename}_video_HQ.mp4")
    (
        ffmpeg
        .input(input_video_path)
        .output(video_output_path, vf="scale=-2:1080", r=30, b="5000k")
        .run()
    )

    # Create a video stream at 5fps & 1kbit
    video_stream_output_path = os.path.join(output_directory, f"{base_filename}_video_LQ.mp4")
    (
        ffmpeg
        .input(input_video_path)
        .output(video_stream_output_path, vf="fps=5", r=5, b="1000k")
        .run()
    )

    # Create a jpg stream @ 5fps
    jpg_output_directory = os.path.join(output_directory, f"{base_filename}_jpg_frames")
    os.makedirs(jpg_output_directory, exist_ok=True)
    (
        ffmpeg
        .input(input_video_path)
        .output(os.path.join(jpg_output_directory, "%d.jpg"), vf="fps=5")
        .run()
    )

    print("Processing complete.")
