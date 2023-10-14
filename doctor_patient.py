# import streamlit as st
# st.title("Doctor Patient App")

import whisper

def convert_audio_to_text(audio_file):
    model = whisper.load_model("base")
    result = model.transcribe(audio_file)
    print(result["text"])

convert_audio_to_text("Test.wav")

