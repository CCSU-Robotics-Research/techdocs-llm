from openai import OpenAI
from pydub import AudioSegment

def transcribe(audio_file_path):
    client = OpenAI()

    with open(audio_file_path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            prompt="Be sure to spell the following terms correctly: ABB, IRB-1200, FlexPendant, Mode Switch, Service Port, RobotWare, RAPID."
        )

    output_file_path = audio_file_path.replace('.mp3', '_transcription.txt')
    with open(output_file_path, "w") as f:
        f.write(transcription.text)
        print("Transcription saved to:", output_file_path)

    return transcription.text
