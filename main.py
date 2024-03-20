# Main Runner/CLI
import os
from processVideo import process_video

def main():
    input_directory = "input"
    input_video_path = input("Enter the name of the input video file (located in '/input' directory): ")
    full_input_path = os.path.join(input_directory, input_video_path)

    if not os.path.exists(full_input_path):
        print("File not found. Please make sure the file exists in the '/input' directory.")
        return

    print(f"Starting to process '{input_video_path}' located at '{full_input_path}'.")
    process_video(full_input_path)
    print(f"Audio and video transcode complete.")

if __name__ == "__main__":
    main()
