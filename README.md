# techdocs-llm
Video → Tech Docs utilizing various AI models for text &amp; photo/video

## Requirements

FFmpeg - Latest Version https://ffmpeg.org

## Setup

Install FFmpeg using the link above

```pip install -r requirements.txt``` - to install program dependencies. 

If installing Tkinter gives an error, try to use the package manager built in the PyCharm IDE. Else, you will need to use an external package manager (such as Homebrew) or try installing a package manually (using pip) in the PyCharm terminal. Despite successful installation, you may see a warning in PyCharm saying "Package requirement 'tkinter' is not satisfied" — if the program still runs and displays a GUI window, you can safely ignore this warning.

run ```python main.py``` - to run the program. The main page of the GUI should launch.

The OpenAI API key needs to be saved as an env variable on your machine.