from openai import OpenAI
from pydub import AudioSegment

def transcribe(audio_file_path):
    client = OpenAI()
    #
    # with open(audio_file_path, "rb") as audio_file:
    #     transcription = client.audio.transcriptions.create(
    #         model="whisper-1",
    #         file=audio_file,
    #         prompt="Be sure to spell the following terms correctly: ABB, IRB-1200, FlexPendant, Mode Switch, Service Port, RobotWare, RAPID."
    #     )
    #
    # output_file_path = audio_file_path.replace('.mp3', '_transcription.txt')
    # with open(output_file_path, "w") as f:
    #     f.write(transcription.text)
    #     print("Transcription saved to:", output_file_path)

    # Split file into 10-min segments
    audio_file = AudioSegment.from_mp3(audio_file_path)
    ten_minutes = 10 * 60 * 1000
    segments = audio_file[::ten_minutes]

    # Initial prompting
    system_prompt = "You are a lab technician in an industrial robotics research lab working with ABB robots. Your job is to correct any spelling mistakes in the transcribed text. Make sure that the following key terms are spelled correctly: FlexPendant, IRB-1200, IRC-5. Only add necessary punctuation such as periods, commas, and capitalization, and use only the provided context."
    llm_messages = [
        {
            "role": "system",
            "content": system_prompt
        }
    ]

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

    # Add full transcription to gpt-4 message and send for corrections
    # llm_messages.append({
    #     "role": "user",
    #     "content": full_transcription
    # })
    #
    # response = client.chat.completions.create(
    #     model="gpt-4-turbo-preview",
    #     messages=llm_messages
    # )

    # Save transcription with timestamps as a .txt file
    output_file_path = audio_file_path.replace('_audio.mp3', '_transcription.txt')
    with open(output_file_path, "w") as f:
        f.write(full_transcription)
        print("Transcription saved to:", output_file_path)

    # Turn transcription into work documentation. First create messages to send to OpenAI API
    system_prompt = "You are a lab technician in an industrial robotics research lab working with ABB robots. Your job is to create work documentation based on transcriptions of video tutorials recorded in the lab. Make sure that the following key terms are spelled correctly: FlexPendant, IRB-1200, IRC-5. Work documentation should be created using the markdown language."
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
        print("Markdown saved to:", output_file_path)

    return output_file_path