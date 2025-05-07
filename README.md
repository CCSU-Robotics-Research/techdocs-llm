# LLM in Workforce: Knowledge Capture and Transfer

Video → Tech Docs utilizing AI for technical documentation creation and human input to insert images.

The Video to Technical Documentation Generator is a desktop application that converts instructional videos into detailed technical documentation and allows the user to insert images. It uses AI to transcribe audio, analyze video content, generate structured documentation, and creates placeholders for images that th euser will select.

## Usage:

This system accepts only .mov, .mp4, .avi, and .mkv files. All other file types are rejected.

Drag and drop a valid video file or choose a video file to upload using the system file explorer. Confirm the video you want to process is correct and, optionally, provide context regarding the content of the video. Then, the system will process the video into work instructions with image placeholders. The system will show the user a description of an ideal image and multiple images for each placeholder. All output is saved in the directory of the user's choosing.

Subsequent runs of the video should be saved in a new file location as the system will overwrite the files of the directory.

**Note:** Processing a 10 minute video costs about $0.30 and around 5 minutes.

## System/OS Package Requirements:
Windows 10/11, macOS or Linux are required for this system to operate.

If you are on windows you must follow these steps:

- Download the MSYS2 installer [from msys2.org](https://www.msys2.org/). Get the msys2-x86_64-*.exe installer for 64-bit systems 
- Run the installer
- Once you reach the terminal run this command: pacman -S mingw-w64-x86_64-pango
- For more information visit https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#installation


You must have these packages installed to your local machine prior to installing any Python packages.

- **Python**: Install the latest version of Python from https://python.org. Verify Python is installed with `python --version`. Python version 3.11 or newer is required. 
- **FFmpeg**: Install the latest version from https://ffmpeg.org, or use the Homebrew package manager. Verify FFmpeg is installed on your system with `ffmpeg -version`.
- **tkinter:** Tkinter should already be included as a part of Python. However, to install tkinter, use `sudo apt-get install python3-tk`. If that doesn't work, try `pip install tk`. To verify installation of tkinter, run `python -m tkinter` in the Terminal. If you see a GUI window popup, then Tkinter is installed on your system. _(NOTE: Despite successful installation, you may see a warning in PyCharm saying "Package requirement 'tkinter' is not satisfied" — if the program still runs and displays a GUI window, you can safely ignore this warning.)_

## Python Package Requirements:
To install all the below requirements, use `pip install -r requirements.txt`, or use `pip install <package-name>` and install each package separately.

- **ffmpeg-python**: FFmpeg wrapper for Python. Ensure the FFmpeg package is installed on your system, see above.
- **openai:** The OpenAI client library to access the API.
- **pydub:** Used for audio processing, often requiring FFmpeg. Verify FFmpeg is installed, see above.
- **markdown:** Used for markdown file processing for page generation.
- **tkinterdnd2:** This is a drag-and-drop library for Tkinter.
- **pillow:** This assists in displaying images on the frontend.
- **weasyprint:** Used to convert HTML to PDF.
- **pdf2docx:** Used to convert PDF to DOCX.
- **tkinterweb:** Used to display the HTML.

## Setup:

The OpenAI API key needs to be saved as an environment variable on your machine. On Linux/MacOS use:
`export OPENAI_API_KEY='your_api_key_here'`

then restart terminal and confirm it was set with:
`echo $OPENAI_API_KEY`

On Windows use:
`set OPENAI_API_KEY=your_api_key_here`

then restart terminal and confirm it was set with:
`echo %OPENAI_API_KEY%`

If that doesn't work, then create a file named ".env" in the root folder of the cloned GitHub repository (it should be a hidden file). In the file, write the text `OPENAI_API_KEY=<your-api-key-here>`.  <br />

Then navigate to `transcribe.py` and replace the `client = OpenAI()` code statement with the following code block: 

`from dotenv import load_dotenv` <br />
`import os`

`load_dotenv(dotenv_path=".env")` <br />
`client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))`

If you use this code snippet for a custom .env file in your repo, make sure to exclude these changes when making commits. <br />



1. Clone this git repository to your local machine.
2. Install Python and FFmpeg with the links above.
3. Ensure tkinter is installed on your system; if not then install it.
4. Run `pip install -r requirements.txt` to install all Python package dependencies.
5. Run `python main.py` to execute the program, or click the Play button in PyCharm or with the Python extension in VS Code with the run configuration set to main.py. The main page of the GUI should launch.


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
  - `parse_first_time()`: Gets the start time from each interval in the generated text file
  - `image_selection()`: Starts the process of being able to select images
  - `load_images()`:  Loads the images and corrects their size
  - `display_images()`: Displays images and the alt text to the front end
  - `configure_frame()`: Creates a scrollable frame
  - `select_image()`: Selected images get stored in the correct folder
  - `change_State()`: State of state variable is changed
  - `process_video()`: Communicate with backend.py to initiate video processing for a given video file
  - `extract_images()`: Asks back end to start pulling images
  - `go_back_to_main_page()`: Clear the main frame and reinitialize the main page
  - `start_frontend()`: Driver for GUI initialization, to be invoked in main.py

### `backend.py`
The driver of the video processing (occurring in the background after a video is uploaded) which also depends on other files for assistance.

- `generate_documentation_from_video()`: Given an input video from the GUI (its file path and file name), process it into work instructions.
- `extract_interval_frames()`: Send HTML file and the transcription to AI to find correct time intervals
- `generate_new_images()`: Generates new images if two images are selected
- `convert_html()`: Converts the HTML to DOCX and PDF

### `processVideo.py`
Contains code for transcoding a video into audio and extracting intervals of images from a video with FFmpeg.

- `transcode_audio()`: # Transcode a video to audio file with CD quality .mp3
- `interval_frame_extraction()`: Extract frames @ 1 FPS at all time intervals specified, returning all output directories in an array
- `preliminary_video_processing()`: The first part of video processing: transcoding and creating the output directory

### `transcribe.py`
Contains functions to generate a segmented transcription from an audio file and to find the correct time intervals in the video for image extraction.

- `transcribe()`: Transcribes an audio file into a transcription with timestamps and generates a markdown file
- `obtain_time_intervals()`: Fetches the correct time intervals for image extraction using the generated HTML file with img placeholders and the transcription with timestamps.
- `process_entry()`: Formatting for time intervals
- `validate_interval():` Makes sure the interval is valid (example of invalid is 1:00-1:00)

### `generatePage.py`
Contains functions to generate an HTML page of work instructions from a processed video.

- `generate_page()`: Using a markdown file, generate an HTML page as output
- `numbered_replacement()`: Adjusts markdown image placeholders to HTML images tags
