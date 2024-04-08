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

    # split file into 10-min segments
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

    # transcribe each segment and add it to the full transcription
    previous_transcription = ""
    full_transcription = ""

    for i, segment in enumerate(segments):
        with open("temp/segment_%s.mp3" % i, "wb") as f:
            segment.export(f, format="mp3")
            audio_file = open("temp/segment_%s.mp3" % i, "rb")
            previous_transcription = client.audio.transcriptions.create(file=audio_file,
                                                                        model="whisper-1",
                                                                        prompt=previous_transcription,
                                                                        response_format="text")
            full_transcription += previous_transcription

    # add full transcription to gpt-4 message and send for corrections
    llm_messages.append({
        "role": "user",
        "content": full_transcription
    })

    response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=llm_messages
    )

    output_file_path = audio_file_path.replace('.mp3', '_transcription.txt')
    with open(output_file_path, "w") as f:
        f.write(response.choices[0].message.content)
        print("Transcription saved to:", output_file_path)

    return response.choices[0].message.content
