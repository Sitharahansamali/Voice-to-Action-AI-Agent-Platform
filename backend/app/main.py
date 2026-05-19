from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

import shutil
import whisper
import subprocess
from pathlib import Path

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Whisper model
model = whisper.load_model("base")

# upload directory
UPLOAD_DIR = Path("app/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@app.get("/")
async def root():
    return {"message": "Backend running"}


@app.post("/upload-audio")
async def upload_audio(audio: UploadFile = File(...)):

    try:
        # Original uploaded file
        input_path = UPLOAD_DIR / audio.filename

        # Converted wav file
        output_path = UPLOAD_DIR / "converted.wav"

        # Save uploaded audio
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(audio.file, buffer)

        print("Audio saved:", input_path)

        # Convert webm -> wav using ffmpeg
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(input_path),
                str(output_path),
            ],
            check=True,
        )

        print("Audio converted to WAV")

        # Whisper transcription
        result = model.transcribe(str(output_path))

        transcript = result["text"]

        print("Transcript:", transcript)

        return {
            "message": "success",
            "transcript": transcript,
        }

    except Exception as e:
        print("ERROR:", str(e))

        return {
            "message": "error",
            "error": str(e),
        }