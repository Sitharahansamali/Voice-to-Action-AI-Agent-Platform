from fastapi import FastAPI, UploadFile, File , Form
from fastapi.middleware.cors import CORSMiddleware
from transformers import pipeline

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

# Create intent detection pipeline
intent_classifier = pipeline(
    "zero-shot-classification",
    model="facebook/bart-large-mnli"
)

# create function to detect intent
def detect_intent(text: str):

    candidate_labels = [
        "create_reminder",
        "save_note",
        "summarize",
        "memory_search",
        "general_chat"
    ]

    result = intent_classifier(
        text,
        candidate_labels
    )

    return {
        "intent": result["labels"][0],
        "score": float(result["scores"][0])
    }

# upload directory
UPLOAD_DIR = Path("app/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@app.get("/")
async def root():
    return {"message": "Backend running"}

FFMPEG_PATH = r"D:\ffmpeg-master-latest-win64-gpl-shared\ffmpeg-master-latest-win64-gpl-shared\bin\ffmpeg.exe"
@app.post("/upload-audio")
async def upload_audio(audio: UploadFile = File(...), language: str = Form(...)):

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
        
        # Detect language
        _, probs = model.detect_language(mel)
        
        detected_language = max(
            probs,
            key=probs.get
        )
        
        print("Detected language:", detected_language)
        
        # Decode
        if language == "auto":
            options = whisper.DecodingOptions(
                task="transcribe"
            )
        else:
            options = whisper.DecodingOptions(
                language=language,
                task="transcribe"
            )
        
        result = whisper.decode(
            model,
            mel,
            options
        )
        
        transcript = result.text

        intent_result = detect_intent(transcript)

        print("Intent:", intent_result)

        return {
            "message": "success",
            "transcript": transcript,
            "intent": intent_result
        }

    except Exception as e:
        print("ERROR:", str(e))

        return {
            "message": "error",
            "error": str(e),
        }