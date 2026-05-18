from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import shutil
from pathlib import Path

app = FastAPI()

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

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(audio.file, buffer)

    return {
        "message": "Audio uploaded successfully",
        "filename": audio.filename
    }