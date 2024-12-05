# imageAnalysis.py contains functions for the final keyframe selection process from a set of intervals of images. Image analysis uses OpenAI API.

import base64
import glob
import os
import re
import shutil
from openai import OpenAI

client = OpenAI()

# Encodes an image into a base64 string
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Analyses intervals of images, comparing them against their corresponding alt text placeholders, and selects the best keyframes from each interval
def image_analysis(alt_texts, interval_output_directories):

    # Selected keyframes will be saved here
    output_dir = "output"

    # Ensure the number of directories matches the number of prompts
    if len(interval_output_directories) != len(alt_texts):
        print("Error: The number of directories does not match the number of alt texts.")
        return

    # Process each subdirectory at interval_output_directories
    for index, directory in enumerate(interval_output_directories):
        alt_text = alt_texts[index]
        print(f"Processing directory: {directory} with alt text: '{alt_text}'")

        # Find all .jpg files in the current subdirectory
        image_paths = glob.glob(os.path.join(directory, "*.jpg"))
        if not image_paths:
            print(f"No .jpg files found in directory {directory}")
            continue

        # Start with all images in the directory
        remaining_images = image_paths

        # Select the best image in batches until only one image remains
        while len(remaining_images) > 1:

            # Divide remaining images into batches of 4
            batches = [remaining_images[i:i + 4] for i in range(0, len(remaining_images), 4)]
            next_round_images = [] # List to store selected images for the next round

            # Process each batch
            for batch in batches:

                # Encode each image in the batch to base64
                batch_base64 = [encode_image(img) for img in batch]

                # Prepare messages for the current batch with given prompt
                messages = [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": f'Which of the following images best represents "{alt_text}" Respond with a single number only(1, 2, 3,4 ...) and no additional text, always return a value'},
                            *[
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img}"}}
                                for img in batch_base64
                            ]
                        ]
                    }
                ]

                # Send request to OpenAI API (used 4o mini because cheap)
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    max_tokens=300,
                )

                # Parse the response to get the choice (making sure we get numbers only, not any words)
                choice = response.choices[0].message.content
                match = re.search(r'\b\d+\b', choice)
                if match:
                    # Convert from 1-based to 0-based index
                    position = int(match.group(0)) - 1
                    selected_image = batch[position]
                    next_round_images.append(selected_image)
                else:
                    print(f"Unexpected response for batch in directory {directory}: {choice}")

            # Update for the next loop if needed
            remaining_images = next_round_images

        # After the loop, there should only be one image left
        if remaining_images:
            final_best_image = remaining_images[0]
            output_image_path = os.path.join(output_dir, f"frame_{index + 1}.jpg")  # Save as frame_1.jpg, frame_2.jpg, etc.
            
            # Copy the best image to the output
            shutil.copy(final_best_image, output_image_path)
            print(f"Best image from directory {directory} saved as {output_image_path}")
        else:
            print(f"Could not determine the best image in directory {directory}")
