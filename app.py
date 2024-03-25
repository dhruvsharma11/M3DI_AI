from flask import Flask, render_template, request, jsonify, redirect, url_for
import sounddevice as sd
import numpy as np
import wave
import subprocess

app = Flask(__name__)

# Set the default file path for audio recording
DEFAULT_FILE_PATH = "data/audio.wav"

# Hardcoded user credentials
HARDCODED_USER = {"username": "resha", "password": "password"}

# Flag to check if the user is authenticated
authenticated = False

# Record audio and save it to the file path


def record_audio(duration, sample_rate=44100):
    audio_data = sd.rec(int(duration * sample_rate),
                        samplerate=sample_rate, channels=1, dtype=np.int16, device=1)
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

# Login route


@app.route('/login', methods=['GET', 'POST'])
def login():
    global authenticated

    if request.method == 'POST':
        # Check login credentials
        data = request.form
        if data["username"] == HARDCODED_USER["username"] and data["password"] == HARDCODED_USER["password"]:
            authenticated = True
            return redirect(url_for('index'))
        else:
            return render_template('login.html', message="Invalid credentials. Please try again.")

    return render_template('login.html', message="")

# Main route


@app.route('/', methods=['GET'])
def index():
    global authenticated

    if not authenticated:
        return redirect(url_for('login'))

    return render_template('index.html', default_file_path=DEFAULT_FILE_PATH)

# Recording route


@app.route('/record', methods=['POST'])
def record():
    global authenticated

    if not authenticated:
        return jsonify({"error": "User not authenticated"}), 401

    duration = int(request.form['duration'])
    file_path, audio_data = record_audio(duration)

    # Now, call the transcription script using a subprocess
    transcription_script_path = 'doctor_patient.py'

    print(subprocess.run(['python', transcription_script_path, file_path],
                         capture_output=True, text=True, check=True))

    return jsonify(file_path=file_path)

# Sign-out route


@app.route('/logout')
def logout():
    global authenticated
    authenticated = False

    # Redirect to the login page after logging out
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=False)
