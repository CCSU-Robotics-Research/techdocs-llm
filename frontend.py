import os
import tkinter as tk
from tkinter import filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD
from main import main

class ModernRoundedButton(tk.Canvas):
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

    def _on_configure(self, event=None):
        # Only draw the button once when it's first configured
        if not self.drawn:
            self.draw_button(self.color)
            self.drawn = True

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

    def on_click(self, event):
        if self.command:
            self.command()

    def on_hover(self, event):
        self.draw_button(self.hover_color)

    def on_leave(self, event):
        self.draw_button(self.color)

def display_main_page(root):
    # Frame and state variables
    main_frame = tk.Frame(root, bg="#f4f4f9")
    main_frame.pack(fill=tk.BOTH, expand=True)

    def browse_files():
        file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4 *.mov *.avi *.mkv")])
        handle_file_upload(file_path)

    def on_drop(event):
        file_path = event.data.strip("{}")  # Remove curly braces
        handle_file_upload(file_path)

    # Validate that a file was uploaded and that the file type is correct
    def handle_file_upload(file_path):
        valid_extensions = [".mp4", ".mov", ".avi", ".mkv"]
        if not file_path:
            show_error_message("You must select a video file to process.")
        elif not any(file_path.endswith(ext.lower()) for ext in valid_extensions):
            show_error_message("Invalid file. The system only supports video files with extensions .mov, .mp4, .avi, and .mkv.")
        else:
            print(f"Uploaded File: {file_path}")
            # TODO: Create a page confirming this is the file to be processed with a yes button and a back button
            # main(file_path[file_path.rfind("/")+1:]) # Process the video

    def show_error_message(error_message):
        # Replace drag-and-drop box with error message
        canvas_frame.pack_forget()
        button_frame.pack_forget()

        # Error message label
        error_label = tk.Label(main_frame, text=error_message, font=("Segoe UI", 12, "bold"), fg="red", bg="#f4f4f9", wraplength=600, justify="center")
        error_label.pack(pady=20)

        # Back to main page button
        back_button = ModernRoundedButton(main_frame, text="Back to Main Page", command=reset_main_page, width=180, height=50)
        back_button.pack(pady=10)

    def reset_main_page():
        # Clear the main frame and reinitialize the main page
        for widget in main_frame.winfo_children():
            widget.destroy()
        initialize_main_page()

    def initialize_main_page():
        # Header Section
        header = tk.Label(main_frame, text="Video to Instruction Manual", font=("Segoe UI", 18, "bold"), bg="#4CAF50",
                          fg="white", pady=10)
        header.pack(fill=tk.X)

        # Instruction Label
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

    # Initialize the main page
    initialize_main_page()

# Main Tkinter window
root = TkinterDnD.Tk()
root.title("Instruction Manual Creator")
root.geometry("800x500")
root.configure(bg="#f4f4f9")

# Display the main page
display_main_page(root)
root.mainloop() # Run the Tkinter event loop