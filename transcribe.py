from openai import OpenAI
from pydub import AudioSegment
client = OpenAI()

audio_file= open("12_min_audio.mp3", "rb")
transcription = client.audio.transcriptions.create(
  model="whisper-1",
  file=audio_file,
  prompt="Be sure to spell the following terms correctly: ABB, IRB-1200, FlexPendant, Mode Switch, Service Port, RobotWare, RAPID."
)
f = open("12_min_transcription.txt", "w")
f.write(transcription.text)
f.close()
print(transcription.text)