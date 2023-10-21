
# import streamlit as st
# st.title("Doctor Patient App")

import creds
import whisper
from pyannote.audio import Pipeline
from pydub import AudioSegment
import numpy as np
import gc
import torch

import datetime
import subprocess

from pyannote.audio.pipelines.speaker_verification import PretrainedSpeakerEmbedding
embedding_model = PretrainedSpeakerEmbedding( 
    "speechbrain/spkrec-ecapa-voxceleb",
    device=torch.device("cpu"))

from pyannote.audio import Audio
from pyannote.core import Segment

import wave
import contextlib
from sklearn.cluster import AgglomerativeClustering
import numpy as np
from pydub import AudioSegment


pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization-3.0",
    use_auth_token=creds.use_auth_token)

path = "data/audio.wav"

def convert_to_mono(path):
    sound = AudioSegment.from_wav(path)
    sound = sound.set_channels(1)
    mono_path = path
    sound.export(path, format="wav")
    return mono_path

path = convert_to_mono(path)

num_speakers = 2 #@param {type:"integer"}
language = 'English' #@param ['any', 'English']
model_size = 'base' #@param ['tiny', 'base', 'small', 'medium', 'large']


model_name = model_size
if language == 'English' and model_size != 'large':
  model_name += '.en'

model = whisper.load_model(model_size)

result = model.transcribe(path)
segments = result["segments"]

with contextlib.closing(wave.open(path,'r')) as f:
  frames = f.getnframes()
  rate = f.getframerate()
  duration = frames / float(rate)

audio = Audio()

def segment_embedding(segment):
  start = segment["start"]
  # Whisper overshoots the end timestamp in the last segment
  end = min(duration, segment["end"])
  clip = Segment(start, end)
  waveform, sample_rate = audio.crop(path, clip)
  return embedding_model(waveform[None])

embeddings = np.zeros(shape=(len(segments), 192))
for i, segment in enumerate(segments):
  embeddings[i] = segment_embedding(segment)

embeddings = np.nan_to_num(embeddings)

clustering = AgglomerativeClustering(num_speakers).fit(embeddings)
labels = clustering.labels_
for i in range(len(segments)):
  segments[i]["speaker"] = 'SPEAKER ' + str(labels[i] + 1)

def time(secs):
  return datetime.timedelta(seconds=round(secs))

f = open("transcript.txt", "w")

for (i, segment) in enumerate(segments):
  if i == 0 or segments[i - 1]["speaker"] != segment["speaker"]:
    f.write("\n" + segment["speaker"] + ' ' + str(time(segment["start"])) + '\n')
  f.write(segment["text"][1:] + ' ')
f.close()


# def convert_audio_to_text(audio_file):
#     model = whisper.load_model("base")
#     result = model.transcribe(audio_file)
#     print(result["text"])

# convert_audio_to_text("data/audio.wav")


# # apply pretrained pipeline
# diarization = pipeline("data/audio.wav")

# # print the result
# for turn, _, speaker in diarization.itertracks(yield_label=True):
#     print(
#         f"start={turn.start:.1f}s stop={turn.end:.1f}s speaker_{speaker}")

