from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import shutil
import whisper
from pathlib import Path

app = FastAPI()
model = whisper.load_model("base")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



UPLOAD_DIR = Path("app/uploads")

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@app.get("/")
async def root():
    return {"message": "Backend running"}


@app.post("/upload-audio")
async def upload_audio(audio: UploadFile = File(...)):
    
    file_path = UPLOAD_DIR / audio.filename

    # Save upload file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(audio.file, buffer)

    # Transcribe audio
    result = model.transcribe(str(file_path))

    transcript = result["text"]

    print("Transcript:", transcript)

    return {
        "message": "Audio uploaded successfully",
        "transcript": transcript
    }