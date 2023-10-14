import torch
from pyannote.audio import Pipeline
import whisper
import creds

# import streamlit as st
# st.title("Doctor Patient App")


model = whisper.load_model("base")
result = model.transcribe("data/audio.wav", fp16=False)

print(result["text"])


pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization-3.0",
    use_auth_token=creds.use_auth_token)


# apply pretrained pipeline
diarization = pipeline("data/audio.wav")

# print the result
for turn, _, speaker in diarization.itertracks(yield_label=True):
    print(
        f"start={turn.start:.1f}s stop={turn.end:.1f}s speaker_{speaker}")
