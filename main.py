from fastapi import FastAPI, UploadFile, File
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
async def run_python(file: UploadFile = File(...)):
    file_id = str(uuid.uuid4())
    python_file_path = BASE_DIR / f"{file_id}.py"
    midi_file_path = BASE_DIR / f"file.mid"

    if midi_file_path.exists():
        os.remove(midi_file_path)

    try:
        with open(python_file_path, "wb") as f:
            f.write(await file.read())

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
