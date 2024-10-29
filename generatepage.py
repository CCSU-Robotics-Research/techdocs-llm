import markdown
import os
import re


def generate_page(markdown_path):
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
        alt_text = match.group(1)
        placeholder = f'image_{image_counter}.jpg'
        image_counter += 1
        return f'<img src="{placeholder}" alt="{alt_text}" class="border-2 border-gray-300 rounded-lg my-4" style="max-width: 100%; height: auto;">'

    # Replace image placeholders with numbered HTML img tags
    markdown_content = re.sub(
        r'!\[(.*?)\]\(.*?\)',
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
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/tailwindcss@3.4.3/base.min.css">
        <link rel="stylesheet" href="https://unpkg.com/tailwindcss@1.4.6/dist/components.min.css">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@tailwindcss/typography@0.5.13/src/index.min.js">
        <link rel="stylesheet" href="https://unpkg.com/tailwindcss@1.4.6/dist/utilities.min.css">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap" rel="stylesheet">
        <style>
            body {{
                font-family: 'Inter', sans-serif;
            }}
        </style>
    </head>
    <body class="bg-gray-50 text-gray-800 p-8">
        <div class="max-w-5xl mx-auto prose prose-lg my-8">
            <h1 class="text-blue-600 text-center">Technical Documentation</h1>  <!-- Centered heading with blue color -->
            {html_content}
        </div>
    </body>
    </html>
    """

    # Create the path for the output folder
    parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(markdown_path))))
    output_dir = os.path.join(parent_dir, "output")

    # Ensure the output folder exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Generate the output path for the HTML file
    markdown_filename = os.path.splitext(os.path.basename(markdown_path))[0]
    output_path = os.path.join(output_dir, f"{markdown_filename}.html")

    # Write the HTML content to a new file
    with open(output_path, 'w') as file:
        file.write(html_page)

    # Return the output path
    return output_path

# Example usage
generate_page("temp/test/example.md")
