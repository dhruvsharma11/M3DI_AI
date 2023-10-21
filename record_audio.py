import sounddevice as sd
import numpy as np
import wave
from flask import Flask, render_template, request, jsonify, send_file
import os
import io
import datetime

app = Flask(__name__)

# Set the default directory for audio recording
DEFAULT_DIRECTORY = "audio_recordings"


def record_audio(duration, sample_rate=44100):
    audio_data = sd.rec(int(duration * sample_rate),
                        samplerate=sample_rate, channels=1, dtype=np.int16)
    sd.wait()
    return audio_data


def write_wav(audio_data, sample_rate=44100):
    # Create a directory if it doesn't exist
    if not os.path.exists(DEFAULT_DIRECTORY):
        os.makedirs(DEFAULT_DIRECTORY)

    # Generate a unique filename based on timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = os.path.join(DEFAULT_DIRECTORY, f"recording_{timestamp}.wav")

    with wave.open(file_path, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio_data.tobytes())

    return file_path


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/record', methods=['POST'])
def record():
    duration = int(request.form['duration'])
    audio_data = record_audio(duration)
    file_path = write_wav(audio_data)
    return send_file(file_path, attachment_filename=os.path.basename(file_path),
                     mimetype='audio/wav', as_attachment=True, cache_timeout=0)


if __name__ == '__main__':
    app.run(debug=True)
