# techdocs-llm
Video → Tech Docs utilizing various AI models for text &amp; photo/video

The Video to Technical Documentation Generator is a desktop application that automatically converts instructional videos into detailed technical documentation. It uses AI to transcribe audio, analyze video content, and generate structured documentation with relevant screenshots.

## System Package Requirements:
You must have these packages installed to your local machine prior to installing any Python packages.

- **Python**: Install the latest version of Python from https://python.org. Verify Python is installed with `python --version`.
- **FFmpeg**: Install the latest version from https://ffmpeg.org, or use the Homebrew package manager. Verify FFmpeg is installed on your system with `ffmpeg -version`.
- **tkinter:** Tkinter should already be included as a part of Python. However, to install tkinter, use `sudo apt-get install python3-tk`. If that doesn't work, try `pip install tk`. To verify installation of tkinter, run `python -m tkinter` in the Terminal. If you see a GUI window popup, then Tkinter is installed on your system.

## Python Package Requirements:
To install all the below requirements, use `pip install -r requirements.txt`, or use `pip install <package-name>` and install each package separately.

- **ffmpeg-python**: FFmpeg wrapper for Python. Ensure the FFmpeg package is installed on your system, see above.
- **openai:** The OpenAI client library to access the API.
- **pydub:** Used for audio processing, often requiring FFmpeg. Verify FFmpeg is installed, see above.
- **markdown:** Used for markdown file processing for page generation.
- **tkinterdnd2:** This is a drag-and-drop library for Tkinter. 

## Setup:

1. Clone this git repository to your local machine and set it up in the PyCharm IDE.
2. Install Python and FFmpeg with the links above. Verify these have installed.
3. Ensure tkinter is installed on your system; if not then install it.
4. Run `pip install -r requirements.txt` to install all Python package dependencies.
5. Run `python main.py` to execute the program, or click the Play button in PyCharm with the run configuration set to main.py. The main page of the GUI should launch.

The OpenAI API key needs to be saved as an env variable on your machine. You can export an environment variable from the Terminal with the name `OPENAI_API_KEY`.

If that doesn't work, navigate to `transcribe.py` and replace the `client = OpenAI()` code statement with the following code block: 

`from dotenv import load_dotenv` <br />
`import os`

`load_dotenv(dotenv_path=".env")` <br />
`client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))`

If you use this code snippet for a custom .env file in your repo, make sure to exclude these changes when making commits. <br />

## Source Control Techniques:

It is strongly recommended to use the PyCharm GitHub integration or GitHub Desktop. Only as a last resort (if neither approach of version control works), carefully use git commands in the Terminal. You may need to authenticate with a Personal Access Token (PAT) from your GitHub account prior to pulling or pushing any code with `git`. For details see https://github.com.

To install git on your system, run `brew install git`.

## Developer Table of Contents:

### `main.py`
The entry point of the program. The frontend GUI is launched from here, which then drives backend processes logged in the Terminal.

- `main()`: Starts the frontend GUI upon program launch. The user then interacts with the GUI to process videos.

### `frontend.py`
Contains all the functions that handle the GUI, using the Tkinter library.

- `class ModernRoundedButton()`: Declares a custom button template to be used throughout the GUI.
  - `__init__()`: Creates a ModernRoundedButton with some properties inherited from the Tkinter Canvas, a custom text, a specified command to do something, and a standard width, height, radius, color, hover color, and background color.
  - `draw_button()`: Draws a button with a custom color.
  - `_on_configure()`: Event Handler - When a button is initialized, draw it once.
  - `on_click()`: When the button is clicked, do its respective command.
  - `on_hover()`: When the cursor hovers over the button, change the color to the hover color.
  - `on_leave()`: When the cursor leaves the button, change the color back to normal
- `display_main_page()`: Displays the main page of the GUI
  - `initialize_main_page()`: Construct the main page
  - `browse_files()`: Opens the system file explorer for uploading a video
  - `on_drop()`: Event handler for dragging a video into the GUI
  - `handle_file_upload()`: Validate that a file was actually uploaded/selected and that the file type is correct
  - `show_error_message()`: Error message page with a custom error message
  - `show_confirmation_message():` Page to confirm from user that the selected video is what they want processed (given a video file path)
  - `show_success_message()`: Page to show success message with instructions to save outputted files (at the specified output directory) and a button to go back to the main page
  - `process_video()`: Communicate with backend.py to initiate video processing for a given video file
  - `go_back_to_main_page()`: Clear the main frame and reinitialize the main page
- `start_frontend()`: Driver for GUI initialization, to be invoked in main.py

### `backend.py`
The driver of the video processing (occurring in the background after a video is uploaded) which also depends on other files for assistance.

- `generate_documentation_from_video()`: Given an input video from the GUI (its file path and file name), process it into work instructions.

### `processVideo.py`
Contains code for transcoding a video into audio and extracting intervals of images from a video with FFmpeg.

- `transcode_audio()`: # Transcode a video to audio file with CD quality .mp3
- `interval_frame_extraction()`: Extract frames @ 1 FPS at all time intervals specified, returning all output directories in an array
- `preliminary_video_processing()`: The first part of video processing: transcoding and creating the output directory

### `transcribe.py`
Contains functions to generate a segmented transcription from an audio file and to find the correct time intervals in the video for image extraction.

- `transcribe()`: Transcribes an audio file into a transcription with timestamps and generates a markdown file
- `obtain_time_intervals()`: Fetches the correct time intervals for image extraction using the generated HTML file with img placeholders and the transcription with timestamps.

### `generatePage.py`
Contains functions to generate an HTML page of work instructions from a processed video.

- `generate_page()`: Using a markdown file, generate an HTMl page as output

### `imageAnalysis.py`
Contains functions for the final keyframe selection process from a set of intervals of images. Image analysis uses OpenAI API.

- `encode_image()`: Encodes an image into a base64 string
- `image_analysis()`: Analyses intervals of images, comparing them against their corresponding alt text placeholders, and selects the best keyframes from each interval