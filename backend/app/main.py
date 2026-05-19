from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

import os

os.environ["PATH"] += os.pathsep + r"D:\ffmpeg-master-latest-win64-gpl-shared\ffmpeg-master-latest-win64-gpl-shared\bin\ffmpeg.exe"

import shutil
import whisper
import subprocess
import librosa
import torch

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

FFMPEG_PATH = r"D:\ffmpeg-master-latest-win64-gpl-shared\ffmpeg-master-latest-win64-gpl-shared\bin\ffmpeg.exe"
@app.post("/upload-audio")
async def upload_audio(audio: UploadFile = File(...)):

    try:
        import uuid

        unique_id = uuid.uuid4().hex

        # Input webm file
        input_path = (
            UPLOAD_DIR / f"{unique_id}.webm"
        ).resolve()

        # Output wav file
        output_path = (
            UPLOAD_DIR / f"{unique_id}.wav"
        ).resolve()

        # Save uploaded audio
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(audio.file, buffer)

        print("Audio saved:", input_path)

        # FFmpeg conversion
        command = [
            FFMPEG_PATH,
            "-y",
            "-i",
            str(input_path),
            "-acodec",
            "pcm_s16le",
            "-ar",
            "16000",
            "-ac",
            "1",
            str(output_path),
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
        )

        print("FFMPEG RETURN CODE:", result.returncode)
        print("FFMPEG STDERR:", result.stderr)

        # Verify wav created
        if not output_path.exists():
            raise Exception("WAV file was not created")

        print("WAV created:", output_path)

        # Load audio using librosa instead of whisper loader
        audio_array, sample_rate = librosa.load(
            str(output_path),
            sr=16000,
            mono=True
        )
        
        # Convert to tensor
        audio_tensor = torch.from_numpy(audio_array)
        
        # Pad or trim
        audio_tensor = whisper.pad_or_trim(audio_tensor)
        
        # Mel spectrogram
        mel = whisper.log_mel_spectrogram(audio_tensor).to(model.device)
        
        # Decode
        options = whisper.DecodingOptions()
        
        result = whisper.decode(model, mel, options)
        
        transcript = result.text
        
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