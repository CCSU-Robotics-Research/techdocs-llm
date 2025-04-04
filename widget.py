import tkinter as tk

root = tk.Tk()
root.title("Multiline Text Field")

# Create a Text widget
text_widget = tk.Text(root, height=10, width=50)
text_widget.pack(padx=10, pady=10)

# Insert default text
text_widget.insert("1.0", "You are a lab technician in an industrial robotics research lab working with ABB robots. Make sure that the following key terms are spelled correctly: FlexPendant, IRB-1200, IRC-5.")

# Button to show content
def show_text():
    content = text_widget.get("1.0", "end-1c")  # From line 1, char 0 to end (minus last newline)
    print("You wrote:\n", content)

tk.Button(root, text="Print Text", command=show_text).pack(pady=5)

root.mainloop()
