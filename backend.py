# backend.py is the driver of the video processing (occurring in the background after a video is uploaded) which also depends on other files for assistance.

import os
from transcribe import transcribe
from transcribe import obtain_time_intervals
from processVideo import process_video
from processVideo import interval_frame_extraction
from datetime import datetime
from generatePage import generate_page
from imageAnalysis import image_analysis

# Given an input video from the GUI, process it into work instructions
def generate_documentation_from_video(input_video_path, full_input_path):

    # TODO: Change program code dependencies so any video in any directory can be processed (i.e., /input directory not required)
    # For now, check if the specified video exists in the /input directory
    if not os.path.exists(full_input_path):
        print("File not found. Please make sure the file exists in the '/input' directory.")
        return

    # Begin processing the video. First transcode the video and transcribe the audio with timestamps included
    print(f"Starting to process '{input_video_path}' located at '{full_input_path}'.")
    base_filename = os.path.splitext(os.path.basename(input_video_path))[0]
    date_str = datetime.now().strftime('%Y%m%d_%H%M%S')
    temp_output_directory = os.path.join("temp", f"{base_filename}_{date_str}")
    audio_path = process_video(full_input_path, base_filename, temp_output_directory)
    print("Audio and video transcode complete.\n")

    # Obtain the markdown and transcription files
    markdown_path, transcription = transcribe(audio_path)

    # Generate the HTML page with keyframe placeholders
    print(f"Generating Page....")
    html_file = generate_page(markdown_path)
    print("Page with keyframe placeholders saved to: " + html_file + "\n")

    # Send the HTML file and transcription (with timestamps) to OpenAI API to find correct time intervals for image extraction
    print("Beginning interval frame extraction...")
    keyframe_time_intervals = obtain_time_intervals(html_file, transcription, base_filename, temp_output_directory)

    # Extract images from the video at the obtained time intervals and capture the directory paths where frames are stored for each interval
    interval_output_directories = interval_frame_extraction(full_input_path, temp_output_directory, base_filename, keyframe_time_intervals)

    # Capture alt texts into a single array
    alt_texts = []
    for (_, alt, _, _) in keyframe_time_intervals:
        alt_texts.append(alt)

    print("Interval frame extraction complete.\n")

    # From each set of images, using the corresponding img placeholder, select the best keyframe and insert it into the HTML file
    print("Beginning keyframe selection and insertion...")
    image_analysis(alt_texts, interval_output_directories)
    print("Keyframe insertion complete.\n")

    # Video processing complete.
    print("Video processing complete.")
    print("Page successfully generated.")
    print("View the Docs with keyframes here: " + html_file)