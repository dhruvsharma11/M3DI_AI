from flask import Flask, render_template, request, jsonify, send_file
import os
import sounddevice as sd
import numpy as np
import wave
import io

app = Flask(__name__)

# Set the default file path for audio recording
DEFAULT_FILE_PATH = "recorded_audio.wav"

# Record audio and save it to the file path


def record_audio(duration, sample_rate=44100):
    audio_data = sd.rec(int(duration * sample_rate),
                        samplerate=sample_rate, channels=1, dtype=np.int16)
    sd.wait()
    write_wav(DEFAULT_FILE_PATH, audio_data)
    return DEFAULT_FILE_PATH, audio_data

# Write audio data to a WAV file


def write_wav(file_path, audio_data, sample_rate=44100):
    with wave.open(file_path, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio_data.tobytes())


@app.route('/')
def index():
    return render_template('index.html', default_file_path=DEFAULT_FILE_PATH)


@app.route('/record', methods=['POST'])
def record():
    duration = int(request.form['duration'])
    file_path, audio_data = record_audio(duration)
    return send_file(io.BytesIO(audio_data.tobytes()),
                     attachment_filename='recorded_audio.wav',
                     mimetype='audio/wav',
                     as_attachment=True,
                     cache_timeout=0), file_path


if __name__ == '__main__':
    app.run(debug=True)
