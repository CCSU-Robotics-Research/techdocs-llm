# generatePage.py contains functions to generate an HTML page of work instructions from a processed video.

import markdown
import os
import re
from tkinter import filedialog
import shutil
# Using a markdown file, generate an HTML page as output
def generate_page(markdown_path):

    # Check if the markdown file exists
    if not os.path.exists(markdown_path):
        raise FileNotFoundError(f"File '{markdown_path}' not found")

    # Read the Markdown content
    with open(markdown_path, 'r') as file:
        markdown_content = file.read()

    # Initialize counter for image numbering
    image_counter = 1

    # Function to replace with numbered placeholders
    def numbered_replacement(match):
        nonlocal image_counter
        alt_text = match.group(1) or f"Image {image_counter} - No description provided"  # Fallback text if alt is empty
        placeholder = f'frame_{image_counter}.jpg'
        image_counter += 1
        return f'<img src="{placeholder}" alt="{alt_text}" style="max-height: 500px; width: auto; border: 2px solid #d1d5db; border-radius: 0.5rem; margin: 1rem 0;">'

    # Replace image placeholders with numbered HTML img tags
    # Updated regex to better handle various markdown image formats
    markdown_content = re.sub(
        r'!\[(.*?)\](?:\((.*?)\))?',  # Matches both ![alt]() and ![alt](url)
        numbered_replacement,
        markdown_content
    )

    # Convert Markdown content to HTML
    html_content = markdown.markdown(markdown_content)

    # Create the HTML structure with Tailwind CSS
    html_page = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Technical Documentation</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap" rel="stylesheet">
        <style>
            body {{
                font-family: 'Inter', sans-serif;
                background-color: #f9fafb; /* Tailwind gray-50 */
                color: #1f2937;            /* Tailwind gray-800 */
                padding: 2rem;
                line-height: 1.6;
            }}
            .container {{
                max-width: 64rem;         /* Tailwind max-w-5xl */
                margin-left: auto;
                margin-right: auto;
                margin-top: 2rem;
                margin-bottom: 2rem;
            }}
            h1.title {{
                color: #2563eb;           /* Tailwind blue-600 */
                text-align: center;
                font-size: 2rem;
                margin-bottom: 1rem;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="title">Technical Documentation</h1>
            {html_content}
        </div>
    </body>
    </html>
    """
    
    # User picks output folder
    folder_selected = filedialog.askdirectory()
    print("LOG :",folder_selected)
    
    
    # Create the path for the output folder
    # parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(markdown_path))))
    # output_dir = os.path.join(parent_dir, "output")

    # # Ensure the output folder exists
    # if not os.path.exists(output_dir):
    #     os.makedirs(output_dir)

    # Generate the output path for the HTML file
   
    markdown_filename = os.path.splitext(os.path.basename(markdown_path))[0]
    print("markdown_filename: ", markdown_filename)
    full_path = os.path.join(folder_selected,f"{markdown_filename}-Folder")
    try:
        folder_for_file_path = os.makedirs(full_path)
        folder_for_file_path = f"{folder_selected}/{markdown_filename}-Folder"
        print("FOLDER_FOR_FILE_PATH: ", folder_for_file_path)
    except FileExistsError:
        folder_for_file_path = f"{folder_selected}/{markdown_filename}-Folder"
        shutil.rmtree(folder_for_file_path)
        os.makedirs(f"{folder_selected}/{markdown_filename}-Folder")
        print(f"One or more directories in '{folder_for_file_path}' already exist.")
    except PermissionError:
        print(f"Permission denied: Unable to create '{folder_for_file_path}'.")
    except Exception as e:
        print(f"An error occurred: {e}")
    #folder_path = os.path.join(folder_selected,folder_for_file_path)
    #print("FOLDER_PATH:  ", folder_path)
    output_path = os.path.join(folder_for_file_path,f"{markdown_filename}.html")
    print("output_path: ", output_path)

    # Write the HTML content to a new file
    with open(output_path, 'w') as file:
        file.write(html_page)

    # Return the output path
    return output_path,folder_for_file_path

# Example usage
# generate_page("temp/test/example.md")
