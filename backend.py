# backend.py is the driver of the video processing (occurring in the background after a video is uploaded) which also depends on other files for assistance.

import os
import shutil
from weasyprint import HTML
from pdf2docx import Converter
from transcribe import transcribe
from transcribe import obtain_time_intervals
from processVideo import preliminary_video_processing
from processVideo import interval_frame_extraction
from datetime import datetime
from generatePage import generate_page

# Given an input video from the GUI, process it into work instructions
def generate_documentation_from_video(input_video_name, full_input_path, prompt):

    # Ensure the input file path exists
    if not os.path.exists(full_input_path):
        print("ERROR: File not found. Please make sure the file path is valid and try again.")
        return

    # Clear the temp directory
    print("LOG: Clearing temp directory")
    for folder_path in os.listdir("temp"):
        try:
            shutil.rmtree(f"temp/{folder_path}")
            print(f"LOG: Deleted: {folder_path}")
        except FileNotFoundError:
            print("LOG: Folder not found.")
        except PermissionError:
            print("LOG: Permission denied. Try running with sudo.")
        except Exception as e:
            print(f"ERROR: {e}")

    # Begin processing the video. First transcode the video and transcribe the audio with timestamps included
    print(f"LOG: Starting to process '{input_video_name}' located at '{full_input_path}'.")
    base_filename = os.path.splitext(os.path.basename(input_video_name))[0]
    date_str = datetime.now().strftime('%Y%m%d_%H%M%S')
    global temp_output_directory
    temp_output_directory = os.path.join("temp", f"{base_filename}_{date_str}")
    audio_path = preliminary_video_processing(full_input_path, base_filename, temp_output_directory)
    print("LOG: Audio and video transcode complete.\n")

    # Obtain the markdown and transcription files
    markdown_path, transcription = transcribe(audio_path, prompt)

    # Generate the HTML page with keyframe placeholders
    print(f"LOG: Generating Page....")
    html_file, selected_folder_path = generate_page(markdown_path)
    print("LOG: Page with keyframe placeholders saved to: " + html_file + "\n")

    # Send the HTML file and transcription (with timestamps) to OpenAI API to find correct time intervals for image extraction
    print("LOG: Beginning interval frame extraction...")
    keyframe_time_intervals, interval_time_txt = obtain_time_intervals(html_file, transcription, base_filename, temp_output_directory)

    # Extract images from the video at the obtained time intervals and capture the directory paths where frames are stored for each interval    
    interval_output_directories = interval_frame_extraction(full_input_path, temp_output_directory, base_filename, keyframe_time_intervals,1)

    # Capture alt texts into a single array
    alt_texts = []
    for (_, alt, _, _) in keyframe_time_intervals:
        alt_texts.append(alt)

    print("LOG: Interval frame extraction complete")

    # Return the image descriptions, file paths to the image directories, and the HTML file to the frontend
    return alt_texts, interval_output_directories, html_file, selected_folder_path, interval_time_txt

def generate_new_images(input_video_path,input_video_name,keyframe_time_intervals, time_interval):
    base_filename = os.path.splitext(os.path.basename(input_video_name))[0]
    return interval_frame_extraction(input_video_path,temp_output_directory,base_filename,keyframe_time_intervals,time_interval)

def convert_html(html_path):
    output_pdf = html_path.replace(".html", ".pdf")
    HTML(filename=html_path).write_pdf(output_pdf)
    print("LOG: PDF conversion complete.")
    
    docx_file = output_pdf.replace(".pdf", ".docx")

    # Create a PDF converter object
    cv = Converter(output_pdf)
    cv.convert(docx_file, start=0, end=None)  # convert all pages
    cv.close()
    print("LOG: DOCX conversion complete.")