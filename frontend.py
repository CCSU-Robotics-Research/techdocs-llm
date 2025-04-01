# frontend.py contains all the functions that handle the GUI, using the Tkinter library.

import os
import tkinter as tk
from tkinter import filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD
from backend import generate_documentation_from_video
from backend import generate_new_images
from PIL import Image, ImageTk
import shutil
import webbrowser
import re

global canvas_frame, button_frame, confirmation_label, filename_label, action_button_frame, back_button, process_button, instruction_frame, state, counter, timestamp_arr, interval_txt

# Class to declare a custom ModernRoundedButton
class ModernRoundedButton(tk.Canvas):
    # Creates a ModernRoundedButton
    def __init__(self, parent, text, command=None, width=150, height=50, radius=25, color="#4CAF50", hover_color="#45a049", bg="#f4f4f9"):
        super().__init__(parent, width=width, height=height, bd=0, highlightthickness=0, relief="flat", bg=bg)
        self.command = command
        self.color = color
        self.hover_color = hover_color
        self.radius = radius
        self.text = text

        # Wait for the widget to be fully created before drawing
        self.bind("<Configure>", self._on_configure)
        self.drawn = False

        self.bind("<Button-1>", self.on_click)
        self.bind("<Enter>", self.on_hover)
        self.bind("<Leave>", self.on_leave)

    # Encapsulation for drawing a button
    def draw_button(self, color):
        self.delete("button")  # Only delete button elements, not everything
        # Add "button" tag to all elements
        self.create_arc(0, 0, self.radius * 2, self.radius * 2, start=90, extent=90, fill=color, outline=color, tags="button")
        self.create_arc(self.winfo_width() - self.radius * 2, 0, self.winfo_width(), self.radius * 2, start=0, extent=90, fill=color, outline=color, tags="button")
        self.create_arc(0, self.winfo_height() - self.radius * 2, self.radius * 2, self.winfo_height(), start=180, extent=90, fill=color, outline=color, tags="button")
        self.create_arc(self.winfo_width() - self.radius * 2, self.winfo_height() - self.radius * 2, self.winfo_width(), self.winfo_height(), start=270, extent=90, fill=color, outline=color, tags="button")
        self.create_rectangle(self.radius, 0, self.winfo_width() - self.radius, self.winfo_height(), fill=color, outline=color, tags="button")
        self.create_rectangle(0, self.radius, self.winfo_width(), self.winfo_height() - self.radius, fill=color, outline=color, tags="button")
        self.create_text(self.winfo_width() / 2, self.winfo_height() / 2, text=self.text, fill="white", font=("Segoe UI", 12, "bold"), tags="button")

    # Event handlers

    # When a button is initialized, draw it once
    def _on_configure(self, event=None):
        if not self.drawn:
            self.draw_button(self.color)
            self.drawn = True

    # When the button is clicked, do its respective action
    def on_click(self, event):
        if self.command:
            self.command()

    # When the cursor hovers over the button, change the color to the hover color
    def on_hover(self, event):
        self.draw_button(self.hover_color)

    # When the cursor leaves the button, change the color back to normal
    def on_leave(self, event):
        self.draw_button(self.color)

# Displays the main page of the GUI
def display_main_page(root):

    # Frame and state variables
    main_frame = tk.Frame(root, bg="#f4f4f9")
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Construct the main page
    def initialize_main_page():

        # Header Section
        header = tk.Label(main_frame, text="Video to Instruction Manual", font=("Segoe UI", 18, "bold"), bg="#4CAF50",
                          fg="white", pady=10)
        header.pack(fill=tk.X)

        # Instruction Label
        global instruction_frame
        instruction_frame = tk.Frame(main_frame, bg="#f4f4f9", pady=20)
        instruction_frame.pack(fill=tk.X)
        instruction_label = tk.Label(instruction_frame,
                                     text="Drag and drop your video file here or use the button below to select a file.",
                                     font=("Segoe UI", 12), bg="#f4f4f9", fg="#333333", wraplength=600,
                                     justify="center")
        instruction_label.pack()

        # Drag-and-Drop Canvas
        global canvas_frame
        canvas_frame = tk.Frame(main_frame, bg="#ffffff", highlightthickness=0)
        canvas_frame.pack(pady=10, ipadx=10, ipady=10)
        canvas = tk.Canvas(canvas_frame, bg="#e8e8e8", highlightthickness=0, width=500, height=200, bd=0)
        canvas.pack()
        canvas.create_rectangle(10, 10, 490, 190, fill="#ffffff", outline="#dddddd", width=2)
        canvas.create_text(250, 100, text="Drag and Drop Video Here", font=("Segoe UI", 14, "italic"), fill="#bbbbbb")
        canvas.drop_target_register(DND_FILES)
        canvas.dnd_bind('<<Drop>>', on_drop)

        # Browse Files Button
        global button_frame
        button_frame = tk.Frame(main_frame, bg="#f4f4f9")
        button_frame.pack(pady=10)
        browse_button = ModernRoundedButton(button_frame, text="Browse Files", command=browse_files, width=180,
                                            height=50)
        browse_button.pack()

        # Footer Section
        footer = tk.Label(main_frame, text="© 2024 The CS MJRS Team | CCSU Robotics Research", font=("Segoe UI", 10),
                          bg="#f4f4f9", fg="#999999", pady=10)
        footer.pack(side=tk.BOTTOM, fill=tk.X)

    # Opens the system file explorer for uploading a video
    def browse_files():
        global video_path
        video_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4 *.mov *.avi *.mkv")])
        handle_file_upload(video_path)

    # Event handler for dragging a video into the GUI
    def on_drop(event):
        global video_path
        video_path = event.data.strip("{}")  # Remove curly braces
        handle_file_upload(video_path)

    # Validate that a file was actually uploaded/selected and that the file type is correct
    def handle_file_upload(video_path):
        valid_extensions = [".mp4", ".mov", ".avi", ".mkv", ".MOV", ".MP4", ".AVI", ".MKV"]
        _, file_extension = os.path.splitext(video_path)

        if not video_path:
            print("LOG: File Explorer opened, no file selected")
            show_error_message("You must select a video file to process.")
        elif file_extension.lower() not in valid_extensions:
            print(f"LOG: Uploaded Bad File: {video_path}")
            show_error_message("Invalid file. The system only supports video files with extensions .mov, .mp4, .avi, and .mkv.")
        else:
            print(f"LOG: Uploaded Video File: {video_path}")
            show_confirmation_message(video_path)

    # Error message page with a custom error message for invalid file uploads
    def show_error_message(error_message):

        # Replace drag-and-drop box with error message
        canvas_frame.pack_forget()
        button_frame.pack_forget()

        # Error message label
        error_label = tk.Label(main_frame, text=error_message, font=("Segoe UI", 12, "bold"), fg="red", bg="#f4f4f9", wraplength=600, justify="center")
        error_label.pack(pady=20)

        # Back to main page button
        back_button = ModernRoundedButton(main_frame, text="Back to Main Page", command=go_back_to_main_page, width=180, height=50)
        back_button.pack(pady=10)

    # Page to confirm from user that the selected video is what they want processed
    def show_confirmation_message(video_path):

        # Extract filename from file path
        filename = video_path.split("/")[-1]

        # Replace drag-and-drop box with confirmation message
        canvas_frame.pack_forget()
        button_frame.pack_forget()

        # Confirmation message label
        global confirmation_label
        confirmation_label = tk.Label(main_frame, text=f"Please confirm: Is this the video file you want to process?", font=("Segoe UI", 12, "bold"), fg="blue", bg="#f4f4f9", wraplength=600, justify="center")
        confirmation_label.pack(pady=10)

        # Video filename label
        global filename_label
        filename_label = tk.Label(main_frame, text=f"Video File: {filename}\nLocated At Path: {video_path}", font=("Segoe UI", 11), fg="#333333", bg="#f4f4f9", wraplength=600, justify="center")
        filename_label.pack(pady=5)
        
        # Action buttons
        global action_button_frame
        action_button_frame = tk.Frame(main_frame, bg="#f4f4f9")
        action_button_frame.pack(pady=10)

        # Back to main page button
        global back_button
        back_button = ModernRoundedButton(action_button_frame, text = "No, Back to Main Page", command=go_back_to_main_page, width=180, height=50)
        back_button.grid(row=0, column=0, padx=10)

        # Start video processing button
        global process_button
        process_button = ModernRoundedButton(action_button_frame, text="Process Video", command=lambda: process_video(video_path), width=180, height=50)
        process_button.grid(row=0, column=1, padx=10)

    # Page to show success message with instructions to save outputted files (at the specified output directory) and a button to go back to the main page
    def show_success_message(output_directory):

        # Replace confirmation message with success message
        global confirmation_label, filename_label, action_button_frame, back_button, process_button
        confirmation_label.pack_forget()
        filename_label.pack_forget()
        action_button_frame.pack_forget()
        back_button.pack_forget()
        process_button.pack_forget()

        # Success message label
        success_label = tk.Label(main_frame, text="Video Processing Successful!", font=("Segoe UI", 12, "bold"), fg="green",
                               bg="#f4f4f9", wraplength=600, justify="center")
        success_label.pack(pady=20)

        # Instructions label
        instructions_label = tk.Label(main_frame, text=f"Documentation and Keyframes Saved To:\n{output_directory}\n\nNavigate to this directory and move the newly generated .html file (and corresponding keyframe images) to an external location before processing another video. Failure to do so will cause your output files to be overwritten in subsequent video processes.",
                                    font = ("Segoe UI", 11), fg = "#333333", bg = "#f4f4f9", wraplength = 600, justify = "center")
        instructions_label.pack(pady=5)

        # Back to main page button
        back_button = ModernRoundedButton(main_frame, text="Back to Main Page", command=go_back_to_main_page,
                                            width=180, height=50)
        back_button.pack(pady=10)

        # Opens HTML File to web browser
        webbrowser.open_new_tab(output_directory)
        print("LOG: Open HTML")
        
    # Function to parse the first time from the text file
    def parse_first_time(frame_number, file_content):
        with open(file_content, 'r') as file:
            lines = file.readlines()
        for line in lines:
         if f"[frame_{frame_number}]" in line:
            parts = line.split(']')
            if len(parts) > 1:
                time_part = parts[1].strip().split('-')[0]
                try:
                    return float(time_part)
                except ValueError:
                    raise ValueError(f"Invalid time format in frame {frame_number}")
        file.close()
        raise ValueError(f"Frame {frame_number} not found in the content")
    
    # Creates the image selection interface
    def image_selection(alt_texts, directories, html_file, output_dir):
        global state
        state = False
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        index = 0  # Current index of alt_texts and directories
        
        def load_images(directory):
            # Loads images from a directory and returns a list of PhotoImage objects
            images = []
            for filename in os.listdir(directory):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    img_path = os.path.join(directory, filename)
                    try:
                        image = Image.open(img_path)
                        width, height = image.size
                        image = image.resize((width//10, height//10), Image.Resampling.LANCZOS)  # Resize images
                        photo = ImageTk.PhotoImage(image)
                        images.append((photo, img_path))
                    except Exception as e:
                        print(f"ERROR: Error loading image: {img_path}, {e}")
            return images

        def display_images():
            global counter
            counter = 0
            global timestamp_arr
            timestamp_arr = []
            
            # Displays the images in a grid and the alt text
            nonlocal index
            if index >= len(alt_texts):
                show_success_message(html_file)
                return

            alt_label.config(text=alt_texts[index])

            # Clear existing buttons
            for widget in image_frame.winfo_children():
                widget.destroy()

            images = load_images(directories[index])
            row, col = 0, 0
            for photo, img_path in images:
                button = tk.Button(image_frame, image=photo, command=lambda f=img_path: select_image(f))
                button.image = photo  # Keep a reference to prevent garbage collection
                button.grid(row=row, column=col, padx=5, pady=5)
                col += 1
                if col >= 4:  # 4 columns per row
                    col = 0
                    row += 1
    
        def select_image(img_path):
            global state
            global counter
            global interval_txt
            global timestamp_arr
            
            file_num = int(os.path.splitext(os.path.basename(img_path))[0])
            if (not state):
                # Copies the selected image to the output directory and moves to the next set
                nonlocal index
                shutil.copy(img_path, os.path.join(output_dir, f"frame_{index+1}.jpg"))
                index += 1
                display_images()
            else:
                if counter < 2:
                    parse =  parse_first_time(index+1,interval_txt)
                    timestamp_arr.append(parse+(file_num-1))
                    counter += 1

                    if counter == 2:
                        fps = 1
                        sorted_times = sorted(timestamp_arr)
                        timestamp_arr_tuple = [(f"frame_{index+1}", "", *sorted_times)]
                        time_difference = sorted_times[1] - sorted_times[0]
                        
                        # Calculate frames per second to get 9 images in the interval
                        fps = 9 / time_difference if time_difference != 0 else float('inf')
                        generate_new_images(video_path,video_path[video_path.rfind("/") +1:],timestamp_arr_tuple,fps)
                        state = not state
                        display_images()

                else:
                    print("LOG: Nothing is being done since counter is too big")
            

        alt_label = tk.Label(main_frame, text="", bg="#f4f4f9")
        alt_label.pack(pady=10)

        image_frame = tk.Frame(main_frame)
        image_frame.pack()

        select_interval_button = ModernRoundedButton(main_frame, command=lambda: changeState(),text="Select Multiple Images", width=180, height=50)
        select_interval_button.pack(pady=10)
        

        display_images()
        
    def changeState():
        global state
        global counter
        if not state:
            counter = 0
        state = not state

    def process_video(video_path):
        # Remove the confirmation page and display the processing video label
        print("LOG: Removing Confirmation Page")
        global confirmation_label, filename_label, action_button_frame, back_button, process_button
        confirmation_label.pack_forget()
        filename_label.pack_forget()
        action_button_frame.pack_forget()
        back_button.pack_forget()
        process_button.pack_forget()
        instruction_frame.pack_forget()
        
        # Add processing video label and select image label
        # print("LOG: Adding processing video label")
        # process_label = tk.Label(main_frame, text="Processing Video...", font=("Segoe UI", 12, "bold"), fg="red", bg="#f4f4f9", wraplength=600, justify="center")
        # process_label.pack(pady=20)
        select_image_label = tk.Label(main_frame, text="Select an image:", font=("Segoe UI", 12, "bold"), fg="red", bg="#f4f4f9", wraplength=600, justify="center")
        select_image_label.pack(pady=10)

        
        # Process the video and obtain image descriptions, directories, and html file
        print(f"LOG: Processing Video from GUI: {video_path}")
        alt_texts, output_direcs, html_file, output_dir, fps_txt = generate_documentation_from_video(video_path[video_path.rfind("/") +1:], video_path)
        global interval_txt
        interval_txt = fps_txt
        # Begin manual image selection
        print("LOG: Beginning manual image selection")
        image_selection(alt_texts, output_direcs, html_file,output_dir)

    # Clear the main frame and reinitialize the main page
    def go_back_to_main_page():
        print("LOG: Reverting to main page")
        for widget in main_frame.winfo_children():
            widget.destroy()
        initialize_main_page()

    initialize_main_page() # Create a main page to be displayed to the user

# Driver for GUI initialization, to be invoked in main.py
def start_frontend():

    # Main Tkinter window
    root = TkinterDnD.Tk()
    root.title("Instruction Manual Creator")
    root.geometry("1280x720")
    root.configure(bg="#f4f4f9")

    # Display the main page
    display_main_page(root)
    root.mainloop() # Run the Tkinter event loop