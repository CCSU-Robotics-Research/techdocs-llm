# processVideo.py contains code for transcoding a video into audio and extracting intervals of images from a video with FFmpeg.

import os
import ffmpeg

# Transcode a video to audio file with CD quality .mp3
def transcode_audio(input_video_path, output_directory, base_filename):
    audio_output_path = os.path.join(output_directory, f"{base_filename}_audio.mp3")
    (
        ffmpeg
        .input(input_video_path)
        .output(audio_output_path, ar=44100, ac=2, ab="192k")
        .run()
    )
    return audio_output_path

# Extract frames @ 1 FPS at all time intervals specified, returning all output directories in an array
def interval_frame_extraction(input_video_path, output_directory, base_filename, keyframe_time_intervals):

    # Output directories, to be returned at end
    jpg_directories = []

    # Extract images at 1 FPS for each selected time interval
    for (frame, alt, start, end) in keyframe_time_intervals:
        jpg_output_directory = os.path.join(output_directory, f"{base_filename}_{frame}_jpg_frames")
        os.makedirs(jpg_output_directory, exist_ok=True)
        (
            ffmpeg
            .input(input_video_path, ss=start, to=end)
            .filter("fps", fps=1) # Extract frames at 1 FPS
            .output(os.path.join(jpg_output_directory, "%d.jpg"), q=2) # Highest image quality
            .run()
        )
        jpg_directories.append(jpg_output_directory)

    return jpg_directories

# The first part of video processing: transcoding and creating the output directory
def preliminary_video_processing(input_video_path, base_filename, output_directory):

    # Create a directory for the processed files
    os.makedirs(output_directory, exist_ok=True)

    # Transcode the video into audio
    audio_output_path = transcode_audio(input_video_path, output_directory, base_filename)
    return audio_output_path