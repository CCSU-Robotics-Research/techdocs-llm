# techdocs-llm
Video → Tech Docs utilizing various AI models for text &amp; photo/video

## Requirements:

FFmpeg - Latest Version https://ffmpeg.org

## Setup:

Install FFmpeg using the link above

```pip install -r requirements.txt``` - to install program dependencies. 

If installing Tkinter gives an error, try to use the package manager built in the PyCharm IDE. Else, you will need to use an external package manager (such as Homebrew) or try installing a package manually (using pip) in the PyCharm terminal. Despite successful installation, you may see a warning in PyCharm saying "Package requirement 'tkinter' is not satisfied" — if the program still runs and displays a GUI window, you can safely ignore this warning.

run ```python main.py``` - to run the program. The main page of the GUI should launch.

The OpenAI API key needs to be saved as an env variable on your machine. You can create a custom .env file and use the `load_dotenv()` function from the `os` module, or you can export an environment variable from the Terminal.

## Developer Table of Contents:

### main.py
The entry point of the program. The frontend GUI is launched from here, which then drives backend processes logged in the Terminal.

- **main():** Starts the frontend GUI upon program launch. The user then interacts with the GUI to process videos.

### frontend.py:
Contains all the functions that handle the GUI, using the Tkinter library.

- **class ModernRoundedButton():** Declares a custom button template to be used throughout the GUI.
  - **\_\_init\_\_():** Creates a ModernRoundedButton with some properties inherited from the Tkinter Canvas, a custom text, a specified command to do something, and a standard width, height, radius, color, hover color, and background color.
  - **draw_button():** Draws a button with a custom color.
  - **\_on_configure():** Event Handler - When a button is initialized, draw it once.
  - **on_click():** When the button is clicked, do its respective command.
  - **on_hover():** When the cursor hovers over the button, change the color to the hover color.
  - **on_leave():** When the cursor leaves the button, change the color back to normal
- **display_main_page():** Displays the main page of the GUI
  - **browse_files():** Opens the system file explorer for uploading a video
  - **on_drop():** Event handler for dragging a video into the GUI
  - **handle_file_upload():** Validate that a file was actually uploaded/selected and that the file type is correct
  - **show_error_message():** Error message page with a custom error message
  - **show_confirmation_message():** Page to confirm from user that the selected video is what they want processed (given a video file path)
  - **process_video():** Communicate with backend.py to initiate video processing for a given video file
  - **reset_main_page():** Clear the main frame and reinitialize the main page
  - **initialize_main_page():** Construct the main page
- **start_frontend():** Driver for GUI initialization, to be invoked in main.py

### backend.py
The driver of the video processing (occurring in the background after a video is uploaded) which also depends on other files for assistance.

- **generate_documentation_from_video():** Given an input video from the GUI (its file path and file name), process it into work instructions.

### processVideo.py
Contains code for transcoding a video into audio and extracting intervals of images from a video with FFmpeg.

- **transcode_audio():** # Transcode a video to audio file with CD quality .mp3
- **interval_frame_extraction():** Extract frames @ 1 FPS at all time intervals specified, returning all output directories in an array
- **preliminary_video_processing():** The first part of video processing: transcoding and creating the output directory

### transcribe.py
Contains functions to generate a segmented transcription from an audio file and to find the correct time intervals in the video for image extraction.

- **transcribe():** Transcribes an audio file into a transcription with timestamps and generates a markdown file
- **obtain_time_intervals():** Fetches the correct time intervals for image extraction using the generated HTML file with img placeholders and the transcription with timestamps.

### generatePage.py
Contains functions to generate an HTML page of work instructions from a processed video.

- **generate_page():** Using a markdown file, generate an HTMl page as output

### imageAnalysis.py
Contains functions for the final keyframe selection process from a set of intervals of images. Image analysis uses OpenAI API.

- **encode_image():** Encodes an image into a base64 string
- **image_analysis():** Analyses intervals of images, comparing them against their corresponding alt text placeholders, and selects the best keyframes from each interval