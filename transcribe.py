# transcribe.py contains functions to generate a segmented transcription from an audio file and to find the correct time intervals in the video for image extraction.

from openai import OpenAI
from pydub import AudioSegment
import json

client = OpenAI() # Instance to access OpenAI API

# Transcribes an audio file into a transcription with timestamps and generates a markdown file
def transcribe(audio_file_path, prompt):

    # Split file into 10-min segments
    audio_file = AudioSegment.from_mp3(audio_file_path)
    ten_minutes = 10 * 60 * 1000
    segments = audio_file[::ten_minutes]

    # Transcribe each segment with timestamps and add it to the full transcription
    full_transcription = ""

    # Process each piece of audio
    for i, segment in enumerate(segments):
        with open("temp/segment_%s.mp3" % i, "wb") as f:
            segment.export(f, format="mp3")
            audio_file = open("temp/segment_%s.mp3" % i, "rb")
            response = client.audio.transcriptions.create(file=audio_file,
                                                          model="whisper-1",
                                                          response_format="verbose_json",
                                                          timestamp_granularities=["segment"])
            # Correct each transcription segment's timestamps and add the segment to the transcription
            if response.segments:
                for item in response.segments:
                    start_time = item.start + (i * ten_minutes / 1000) # Adjust timestamps based on segment offset
                    end_time = item.end + (i * ten_minutes / 1000) # Adjust timestamps based on segment offset
                    text = item.text.strip()
                    full_transcription += f"[{start_time:.2f}-{end_time:.2f}] {text}\n"
            else:
                print("Unable to access JSON data for segments.") # Error reading the API response

    # Save transcription with timestamps as a .txt file
    output_file_path = audio_file_path.replace('_audio.mp3', '_transcription.txt')
    with open(output_file_path, "w") as f:
        f.write(full_transcription)
        print("Transcription saved to: " + output_file_path)

    # Turn transcription into work documentation. First create messages to send to OpenAI API
    print("PROMPT HERE: ",prompt)
    instructions = "Your job is to create work documentation based on transcriptions of video tutorials recorded in the lab. Work documentation should be created using the markdown language."
    system_prompt = prompt + instructions
    llm_messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": "The following is a transcript of an audio recording taken from a robotics research lab. Given the transcript, identify the key points of the recorded demonstration, provide a brief summary of the transcription's overall contents, and create step-by-step instructions for each of the key points or tasks demonstrated in the recording. Explanations and instructions should remain within the context of the transcription. However, ensure that a new user could understand and follow the instructions adequately. Instructions should include visual landmarks such that \"a blind person could follow them\" (i.e. describing the color and location of buttons which need to be pressed, the direction that a knob needs to be turned, etc.). Output should be in markdown language. The next message will contain the transcription"
        },
        {
            "role": "user",
            "content": full_transcription
        },
        {
            "role": "user",
            "content": "Now please add placeholder text wrapped in ![]() markdown image syntax where images from the source video of this demonstration should be added to these instructions to provide visual reference. Each image MUST include descriptive alt text between the square brackets [alt text here]. The alt text should describe what the content of the image should show, relevant to the instruction(s) it corresponds to. If multiple images are required per instruction, each image placeholder should be on its own line. Example format: ![Detailed description of what this image should show]()"
        }
    ]

    # Send the API request
    response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=llm_messages
    )

    # Save the created work instructions as a markdown file
    output_file_path = audio_file_path.replace('_audio.mp3', '_workdocs.md')
    with open(output_file_path, "w") as f:
        f.write(response.choices[0].message.content)
        print("Markdown saved to: ", output_file_path)
        print(output_file_path)
    # Return the HTML file and the transcription with timestamps
    return output_file_path, full_transcription

# Fetches the correct time intervals for image extraction using the generated HTML file with img placeholders and the transcription with timestamps.
def obtain_time_intervals(html_file, transcription, base_filename, output_directory):

    # Read the HTML file with alt text into a string
    html_contents = ""
    with open(html_file, "r") as file:
        html_contents = file.read()

    # Prompt to be sent to OpenAI API
    prompt = """
    You are analyzing a transcript of a robotics lab video with timestamps, as well as an HTML file containing placeholder image tags with descriptive alt text. Each image represents a keyframe that should be captured at a specific interval in the video.

    Your task:
    - Match each image tag’s alt text with the relevant section(s) of the transcript.
    - Identify the best start and end timestamps that correspond to each alt text description, with each start timestamp coming BEFORE its end timestamp (i.e., the end timestamp must be greater than the start timestamp to logically make a time interval).
    - Ensure each time interval is as narrow as possible, just enough to capture the details presented in the alt text without omitting any details. Ideally, the difference between each start and end timestamp should be no more than 5-7 seconds long.
    - Return each matched time interval in the format: [frame_id] start-end | "alt text", where `frame_id` is the order of the image tag in the HTML file (1, 2, 3, etc.), `start-end` represents the timestamp range (each are in seconds, no colon formatting), and '"alt text"' is the corresponding alt text attribute from the img tag in the HTML file.

    Example Format:
    [frame_1] 12.00-15.00 | "Sample alt text"
    [frame_2] 45.00-48.00 | "Sample alt text"

    Do not include any additional text or explanations.
    """

    # Construct messages with file contents included
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": f"Transcript:\n{transcription}"},
        {"role": "user", "content": f"HTML with image tags:\n{html_contents}"}
    ]

    # Call OpenAI API with the constructed messages
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=messages
    )

    # Process the response into an array of tuples to prepare for image extraction
    data = response.choices[0].message.content.split("\n")
    formatted_intervals = [] # Array to store the formatted tuples

    for entry in data:
        # Split the entry by ' | ' to separate the time interval and description
        info = entry.split(" | ")

        # Extract frame name from '[frame_1]'
        frame_name = info[0].split("]")[0][1:]

        # Extract start and end times from interval range
        time_range = info[0].split(" ")[1]
        start_time, end_time = map(float, time_range.split("-"))

        # Create the tuple
        formatted_tuple = (frame_name, info[1].strip('"'), start_time, end_time)
        formatted_intervals.append(formatted_tuple)

    # Validate each interval, end should be greater than start (THIS WILL BE DELETED):
    for i, (frame, description, start, end) in enumerate(formatted_intervals):
        # Swap start and end if end is less than start
        if end < start:
            start, end = end, start  # Swap the times
        # Replace the tuple in the list with the corrected tuple
        formatted_intervals[i] = (frame, description, start, end)

    # Save the captured time intervals in a .txt file as a record
    output_file_path = output_directory + "/" + base_filename + "_keyframe_time_intervals.txt"
    with open(output_file_path, "w") as f:
        f.write(response.choices[0].message.content)
        print("Time interval data saved to: " + output_file_path + "\n")

    # Return the array of tuples
    return formatted_intervals, output_file_path