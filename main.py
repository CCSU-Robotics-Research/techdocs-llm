# Main Runner/CLI
import os
from transcribe import transcribe
from transcribe import obtain_time_intervals
from processVideo import process_video
from processVideo import interval_frame_extraction
from datetime import datetime
from generatePage import generate_page

def main():

    # User input for video to process
    input_directory = "input"
    input_video_path = input("Enter the name of the input video file (located in '/input' directory): ")
    full_input_path = os.path.join(input_directory, input_video_path)

    # Check if the specified video exists
    if not os.path.exists(full_input_path):
        print("File not found. Please make sure the file exists in the '/input' directory.")
        return

    # Begin processing the video. First transcode the video and transcribe the audio with timestamps included
    print(f"Starting to process '{input_video_path}' located at '{full_input_path}'.")
    base_filename = os.path.splitext(os.path.basename(input_video_path))[0]
    temp_output_directory = os.path.join("temp", f"{base_filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    audio_path, video_hq_path, video_lq_path, _ = process_video(full_input_path, base_filename, temp_output_directory)
    print(f"Audio and video transcode complete.")

    # Obtain the markdown and transcription files
    markdown_path, transcription = transcribe(audio_path)

    # Generate the HTML page with keyframe placeholders
    print(f"Generating Page....")
    html_file = generate_page(markdown_path)
    print("Page with keyframe placeholders saved to: " + html_file)

    # Send the HTML file and transcription (with timestamps) to OpenAI API to find correct time intervals for image extraction
    print("Beginning keyframe extraction...")
    keyframe_time_intervals = obtain_time_intervals(html_file, transcription, base_filename, temp_output_directory)

    # Extract images from the video at the obtained time intervals
    interval_output_directories = interval_frame_extraction(full_input_path, temp_output_directory, base_filename, keyframe_time_intervals)

    # Temporary, this will be deleted
    for output in interval_output_directories:
        print(output)

    print("Keyframe extraction complete.")

    # TODO: From each set of images, using the corresponding img placeholder, select the best keyframe and insert it into the HTML file

    # Processing complete.
    # print("Page successfully generated.")
    # print("View the Docs with keyframes here: " + html_file)

if __name__ == "__main__":
    main()
