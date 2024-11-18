import tkinter as tk
from tkinter import filedialog, ttk
from tkinterdnd2 import DND_FILES, TkinterDnD

class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command=None, radius=15, bg_color="#8B0000", hover_color="#A52A2A"):
        super().__init__(parent, bd=0, highlightthickness=0, relief='ridge')
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.radius = radius
        self.command = command
        self.text = text
        
        # Set initial size
        self.width = 120
        self.height = 40
        self.configure(width=self.width, height=self.height)
        
        # Create the rounded rectangle button
        self.draw_button(self.bg_color)
        
        # Bind hover events
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)
        
    def draw_button(self, color):
        self.delete("all")
        # Create rounded corners using arcs
        self.create_arc(0, 0, self.radius*2, self.radius*2, start=90, extent=90, fill=color)
        self.create_arc(self.width-self.radius*2, 0, self.width, self.radius*2, start=0, extent=90, fill=color)
        self.create_arc(0, self.height-self.radius*2, self.radius*2, self.height, start=180, extent=90, fill=color)
        self.create_arc(self.width-self.radius*2, self.height-self.radius*2, self.width, self.height, start=270, extent=90, fill=color)
        
        # Create rectangles to fill the space
        self.create_rectangle(self.radius, 0, self.width-self.radius, self.height, fill=color, outline=color)
        self.create_rectangle(0, self.radius, self.width, self.height-self.radius, fill=color, outline=color)
        
        # Add text
        self.create_text(self.width/2, self.height/2, text=self.text, fill="white", font=("Arial", 10, "bold"))
        
    def on_enter(self, event):
        self.draw_button(self.hover_color)
        
    def on_leave(self, event):
        self.draw_button(self.bg_color)
        
    def on_click(self, event):
        if self.command:
            self.command()

def browse_files():
    file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4 *.mov *.avi *.mkv")])
    if file_path:
        print(file_path)  # Print the file path to the console

def on_drop(event):
    print(event.data)  # Print the file path when a file is dropped

def update_inner_layer():
    width = int(root.winfo_width() * 0.95) - 20  # Shrink by 5% and subtract padding
    height = int(root.winfo_height() * 0.95) - 20  # Shrink by 5% and subtract padding
    
    # Calculate center position
    x_pos = (root.winfo_width() - width) // 2
    y_pos = (root.winfo_height() - height) // 2
    
    inner_canvas.place(x=x_pos, y=y_pos, width=width, height=height)

    # Clear previous rounded shapes
    inner_canvas.delete("all")

    # Create the inner rounded corners with a white background
    inner_radius = 20  # Set the inner radius size to match the outer radius
    inner_canvas.create_oval(0, 0, inner_radius * 2, inner_radius * 2, fill="white", outline="")
    inner_canvas.create_oval(width - inner_radius * 2, 0, width, inner_radius * 2, fill="white", outline="")
    inner_canvas.create_oval(0, height - inner_radius * 2, inner_radius * 2, height, fill="white", outline="")
    inner_canvas.create_oval(width - inner_radius * 2, height - inner_radius * 2, width, height, fill="white", outline="")
    inner_canvas.create_rectangle(inner_radius, 0, width - inner_radius, height, fill="white", outline="")
    inner_canvas.create_rectangle(0, inner_radius, width, height - inner_radius, fill="white", outline="")

# Create the main Tkinter window
root = TkinterDnD.Tk()
root.title("Upload Video")

# Set window size to 720p (1280x720)
root.geometry("1280x720")

# Create a canvas for the window background
canvas = tk.Canvas(root, bg="#ffcccc", highlightthickness=0)
canvas.pack(fill=tk.BOTH, expand=True)

# Draw the outer rounded rectangle (pastel red)
radius = 20
canvas.create_oval(0, 0, radius * 2, radius * 2, fill="#ffcccc", outline="")
canvas.create_oval(1280 - radius * 2, 0, 1280, radius * 2, fill="#ffcccc", outline="")
canvas.create_oval(0, 720 - radius * 2, radius * 2, 720, fill="#ffcccc", outline="")
canvas.create_oval(1280 - radius * 2, 720 - radius * 2, 1280, 720, fill="#ffcccc", outline="")
canvas.create_rectangle(radius, 0, 1280 - radius, 720, fill="#ffcccc", outline="")
canvas.create_rectangle(0, radius, 1280, 720 - radius, fill="#ffcccc", outline="")

# Create a separate canvas for the inner rounded area
inner_canvas = tk.Canvas(root, bg="white", highlightthickness=0, borderwidth=0)
inner_canvas.place(x=10, y=10, width=1280 - 20, height=720 - 20)

# Create the inner rounded corners for the first time
update_inner_layer()

# Instruction Label for Drag and Drop
instruction_label = tk.Label(
    inner_canvas,
    text="Upload video",
    font=("Arial", 25),
    fg="#333333",
    bg="white"  # Background of label matches inner layer
)
instruction_label.place(relx=0.5, rely=0.2, anchor="center")

# Create and pack the custom rounded button with red colors
rounded_button = RoundedButton(inner_canvas, text="Select file", command=browse_files)
rounded_button.place(relx=0.5, rely=0.75, anchor="center")

# Bind the resize event to update the inner layer
root.bind("<Configure>", lambda e: update_inner_layer())

# Run the Tkinter main loop
root.mainloop()