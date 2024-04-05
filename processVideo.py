import os
import ffmpeg
from datetime import datetime
import threading

# Transcode audio to CD quality .mp3
def transcode_audio(input_video_path, output_directory, base_filename):
    audio_output_path = os.path.join(output_directory, f"{base_filename}_audio.mp3")
    (
        ffmpeg
        .input(input_video_path)
        .output(audio_output_path, ar=44100, ac=2, ab="192k")
        .run()
    )
    return audio_output_path

# Transcode video to 1080p 30fps @ 5kbit
def transcode_video_HQ(input_video_path, output_directory, base_filename):
    video_output_path = os.path.join(output_directory, f"{base_filename}_video_HQ.mp4")
    (
        ffmpeg
        .input(input_video_path)
        .output(video_output_path, vf="scale=-2:1080", r=30, b="5000k")
        .run()
    )
    return video_output_path

# Transcode video to 1080p 5fps @ 1kbit
def transcode_video_LQ(input_video_path, output_directory, base_filename):
    video_stream_output_path = os.path.join(output_directory, f"{base_filename}_video_LQ.mp4")
    (
        ffmpeg
        .input(input_video_path)
        .output(video_stream_output_path, vf="fps=5", r=5, b="1000k")
        .run()
    )
    return video_stream_output_path

# Create a jpg stream @ 5fps
def extract_frames(input_video_path, output_directory, base_filename):
    jpg_output_directory = os.path.join(output_directory, f"{base_filename}_jpg_frames")
    os.makedirs(jpg_output_directory, exist_ok=True)
    (
        ffmpeg
        .input(input_video_path)
        .output(os.path.join(jpg_output_directory, "%d.jpg"), vf="fps=5")
        .run()
    )
    return jpg_output_directory

def process_video(input_video_path):
    # Get the base filename of the input video
    base_filename = os.path.splitext(os.path.basename(input_video_path))[0]

    # Create a directory for the processed files
    output_directory = os.path.join("temp", f"{base_filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    os.makedirs(output_directory, exist_ok=True)

    # Multithread transcription
    threads = []

    audio_thread = threading.Thread(target=transcode_audio, args=(input_video_path, output_directory, base_filename))
    threads.append(audio_thread)

    #video_HQ_thread = threading.Thread(target=transcode_video_HQ, args=(input_video_path, output_directory, base_filename))
    #threads.append(video_HQ_thread)

    #video_LQ_thread = threading.Thread(target=transcode_video_LQ, args=(input_video_path, output_directory, base_filename))
    #threads.append(video_LQ_thread)

    #frames_thread = threading.Thread(target=extract_frames, args=(input_video_path, output_directory, base_filename))
    #threads.append(frames_thread)

    # Start all threads
    for thread in threads:
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    print("Processing complete.")

    # Collect and return file names
    audio_output_path = os.path.join(output_directory, f"{base_filename}_audio.mp3")
    video_HQ_output_path = os.path.join(output_directory, f"{base_filename}_video_HQ.mp4")
    video_LQ_output_path = os.path.join(output_directory, f"{base_filename}_video_LQ.mp4")
    jpg_output_directory = os.path.join(output_directory, f"{base_filename}_jpg_frames")

    return audio_output_path, video_HQ_output_path, video_LQ_output_path, jpg_output_directory
