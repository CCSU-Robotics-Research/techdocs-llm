# Main Runner/CLI
import os
from transcribe import transcribe
from processVideo import process_video
from generatePage import generate_page

def main():
    input_directory = "input"
    input_video_path = input("Enter the name of the input video file (located in '/input' directory): ")
    full_input_path = os.path.join(input_directory, input_video_path)

    if not os.path.exists(full_input_path):
        print("File not found. Please make sure the file exists in the '/input' directory.")
        return

    print(f"Starting to process '{input_video_path}' located at '{full_input_path}'.")
    audio_path, video_hq_path, video_lq_path, jpg_frames_path = process_video(full_input_path)
    print(f"Audio and video transcode complete.")

    markdown_path = transcribe(audio_path) #pass the path of the .md file here

    print(f"Generating Page....")
    html_file = generate_page(markdown_path)
    print("View the Docs here: " + html_file)

if __name__ == "__main__":
    main()
