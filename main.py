# Main Runner/CLI
import os
from transcribe import transcribe
from transcribe import obtain_time_intervals
from processVideo import process_video
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
    audio_path, video_hq_path, video_lq_path, jpg_frames_path = process_video(full_input_path)
    print(f"Audio and video transcode complete.")

    # Obtain the markdown and transcription files
    markdown_path, transcription = transcribe(audio_path)

    # Generate the HTML page with keyframe placeholders
    print(f"Generating Page....")
    html_file = generate_page(markdown_path)
    print("View the Docs here: " + html_file)

    # Send the HTML file and transcription (with timestamps) to OpenAI API to find correct time intervals for image extraction
    keyframe_time_intervals = obtain_time_intervals(html_file, transcription)

    for (fr, alt, start, end) in keyframe_time_intervals:
        print(f'[{fr}] {start:.2f}-{end:.2f} | {alt}')

    # TODO: Extract images from the video at the obtained time intervals

    # TODO: From each set of images, using the corresponding img placeholder, select the best keyframe and insert it into the HTML file

if __name__ == "__main__":
    main()
