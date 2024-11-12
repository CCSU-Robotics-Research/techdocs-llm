import os
import ffmpeg
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

# Create a jpg stream @ 1fps
def extract_frames(input_video_path, output_directory, base_filename):
    jpg_output_directory = os.path.join(output_directory, f"{base_filename}_jpg_frames")
    os.makedirs(jpg_output_directory, exist_ok=True)
    (
        ffmpeg
        .input(input_video_path)
        .filter("fps", fps=1) # Extract frames at 1 FPS
        .output(os.path.join(jpg_output_directory, "%d.jpg"))
        .run()
    )
    return jpg_output_directory

# Extract frames @ 1 FPS at all intervals and return all output directories in an array
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

def process_video(input_video_path, base_filename, output_directory):
    # # Get the base filename of the input video
    # base_filename = os.path.splitext(os.path.basename(input_video_path))[0]

    # Create a directory for the processed files
    # output_directory = os.path.join("temp", f"{base_filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    os.makedirs(output_directory, exist_ok=True)

    # Multithread transcription
    threads = []

    # Thread for transcoding video to audio
    audio_thread = threading.Thread(target=transcode_audio, args=(input_video_path, output_directory, base_filename))
    threads.append(audio_thread)

    #video_HQ_thread = threading.Thread(target=transcode_video_HQ, args=(input_video_path, output_directory, base_filename))
    #threads.append(video_HQ_thread)

    #video_LQ_thread = threading.Thread(target=transcode_video_LQ, args=(input_video_path, output_directory, base_filename))
    #threads.append(video_LQ_thread)

    # (OMITTED) Thread for frame extraction from the whole video at 1 FPS
    # frames_thread = threading.Thread(target=extract_frames, args=(input_video_path, output_directory, base_filename))
    # threads.append(frames_thread)

    # Start all threads
    for thread in threads:
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Collect and return file names
    audio_output_path = os.path.join(output_directory, f"{base_filename}_audio.mp3")
    video_HQ_output_path = os.path.join(output_directory, f"{base_filename}_video_HQ.mp4")
    video_LQ_output_path = os.path.join(output_directory, f"{base_filename}_video_LQ.mp4")
    jpg_output_directory = os.path.join(output_directory, f"{base_filename}_jpg_frames")

    return audio_output_path, video_HQ_output_path, video_LQ_output_path, jpg_output_directory