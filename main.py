from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
import subprocess
import os
from pathlib import Path
import uuid
import uvicorn

app = FastAPI()

BASE_DIR = Path("temp_files")
BASE_DIR.mkdir(exist_ok=True)

@app.post("/run-python/")
async def run_python(request: Request):
    # Código Python hardcoded
    payload = await request.json()
    prompt = payload.get("prompt")

    code = """
from midiutil import MIDIFile

tempo = 120
volume = 100

MyMIDI = MIDIFile(5)

track_melody = 0
MyMIDI.addTempo(track_melody, 0, tempo)

track_harmony = 1
MyMIDI.addTempo(track_harmony, 0, tempo)

track_bass = 2
MyMIDI.addTempo(track_bass, 0, tempo)

track_drums = 3
MyMIDI.addTempo(track_drums, 0, tempo)

track_effects = 4
MyMIDI.addTempo(track_effects, 0, tempo)

melody = [
    64, 66, 68, 71, 68, 66, 64, 62,
    64, 67, 69, 72, 69, 67, 64, 62,
    64, 66, 68, 71, 68, 66, 64, 62,
    64, 67, 69, 72, 69, 67, 64, 62
]

harmony = [
    [60, 64, 67], [59, 62, 66], [57, 61, 64], [55, 59, 62],
    [60, 64, 67], [59, 62, 66], [57, 61, 64], [55, 59, 62]
]

bass_line = [
    36, 38, 40, 42, 43, 42, 40, 38,
    36, 38, 40, 42, 43, 42, 40, 38
]

effects = [
    76, 78, 80, 81, 83, 81, 80, 78,
    76, 78, 80, 81, 83, 81, 80, 78
]

def add_pattern(track, pattern, start_time, duration):
    for i, note in enumerate(pattern):
        MyMIDI.addNote(track, 0, note, start_time + i * duration, duration, volume)

def add_chords(track, chords, start_time, duration):
    for i, chord in enumerate(chords):
        for note in chord:
            MyMIDI.addNote(track, 0, note, start_time + i * duration, duration, volume)

def add_drums(track, start_time, duration, length):
    for i in range(length):
        if i % 4 == 0:
            MyMIDI.addNote(track, 9, 36, start_time + i * duration, duration, volume)  # Kick drum
        if i % 2 == 0:
            MyMIDI.addNote(track, 9, 38, start_time + i * duration, duration / 2, volume)  # Snare drum
        MyMIDI.addNote(track, 9, 42, start_time + i * duration, duration / 4, volume)  # Hi-hat

for section in range(8):
    time = section * 16
    add_pattern(track_melody, melody, time, 0.5)
    add_chords(track_harmony, harmony, time, 2)
    add_pattern(track_bass, bass_line, time, 1)
    add_pattern(track_effects, effects, time, 0.5)
    add_drums(track_drums, time, 0.25, 64)

with open("temp_files/file.mid", "wb") as output_file:
    MyMIDI.writeFile(output_file)
"""

    file_id = str(uuid.uuid4())
    python_file_path = BASE_DIR / f"{file_id}.py"
    midi_file_path = BASE_DIR / f"file.mid"

    if midi_file_path.exists():
        os.remove(midi_file_path)

    try:
        # Escrever o código no arquivo Python
        with open(python_file_path, "w") as f:
            f.write(code)

        command = f"pip install midiutil && python {python_file_path}"
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
            text=True
        )

        if result.returncode != 0:
            return {"error": f"Erro ao executar o código Python:\n{result.stderr}"}

        if not midi_file_path.exists():
            return {"error": "Arquivo MIDI não foi gerado pelo código Python."}

        return FileResponse(midi_file_path, media_type="audio/mid", filename="file.mid")

    finally:
        if python_file_path.exists():
            os.remove(python_file_path)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
