import tkinter as tk

root = tk.Tk()
root.title("Editable Text Field")

# Create a StringVar with default text
default_text = tk.StringVar()
default_text.set("You are a lab technician in an industrial robotics research lab working with ABB robots. Make sure that the following key terms are spelled correctly: FlexPendant, IRB-1200, IRC-5.")

# Create the Entry widget with the StringVar
entry = tk.Entry(root, textvariable=default_text, width=40)
entry.pack(padx=10, pady=10)

# Optional: Button to print current text
def show_input():
    print("You entered:", entry.get())

tk.Button(root, text="Submit", command=show_input).pack(pady=5)

root.mainloop()
