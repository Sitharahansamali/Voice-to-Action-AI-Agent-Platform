import os
import shutil
import subprocess
import uuid
from pathlib import Path
import whisper

# Global whisper model instance
_whisper_model = None

def get_whisper_model():
    global _whisper_model
    if _whisper_model is None:
        print("Loading Whisper base model...")
        _whisper_model = whisper.load_model("base")
    return _whisper_model

def get_ffmpeg_path():
    # 1. System PATH
    ffmpeg_in_path = shutil.which("ffmpeg")
    if ffmpeg_in_path:
        return ffmpeg_in_path
    
    # 2. Known local Windows fallbacks
    fallbacks = [
        r"D:\ffmpeg-master-latest-win64-gpl-shared\ffmpeg-master-latest-win64-gpl-shared\bin\ffmpeg.exe",
        r"C:\ffmpeg\bin\ffmpeg.exe",
        r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
    ]
    for path in fallbacks:
        if os.path.exists(path):
            return path
            
    return "ffmpeg"

def ensure_ffmpeg_in_path():
    ffmpeg_bin = get_ffmpeg_path()
    ffmpeg_dir = os.path.dirname(ffmpeg_bin)
    if ffmpeg_dir and os.path.exists(ffmpeg_dir):
        path_env = os.environ.get("PATH", "")
        if ffmpeg_dir not in path_env:
            os.environ["PATH"] = ffmpeg_dir + os.pathsep + path_env
    return ffmpeg_bin

def transcribe_audio_file(file_bytes: bytes, filename: str, language: str = "auto", upload_dir: Path = None) -> dict:
    if upload_dir is None:
        upload_dir = Path("app/uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)

    if not file_bytes or len(file_bytes) < 100:
        return {
            "text": "",
            "detected_language": "en",
            "language_used": language,
            "error": "Audio recording is empty or too short."
        }

    unique_id = uuid.uuid4().hex
    ext = "webm"
    fn_lower = filename.lower()
    if "wav" in fn_lower:
        ext = "wav"
    elif "mp4" in fn_lower or "m4a" in fn_lower:
        ext = "mp4"
    elif "ogg" in fn_lower:
        ext = "ogg"

    input_path = (upload_dir / f"{unique_id}.{ext}").resolve()
    output_wav = (upload_dir / f"{unique_id}.wav").resolve()

    with open(input_path, "wb") as buffer:
        buffer.write(file_bytes)

    ffmpeg_bin = ensure_ffmpeg_in_path()
    model = get_whisper_model()

    # 1. ALWAYS convert input file (.webm, .mp4, .ogg, etc.) to 16kHz PCM WAV first via FFmpeg
    conversion_successful = False
    try:
        command = [
            ffmpeg_bin,
            "-y",
            "-i", str(input_path),
            "-acodec", "pcm_s16le",
            "-ar", "16000",
            "-ac", "1",
            str(output_wav)
        ]
        sub_res = subprocess.run(command, capture_output=True, text=True)
        if sub_res.returncode == 0 and output_wav.exists() and output_wav.stat().st_size > 0:
            conversion_successful = True
            print(f"FFmpeg successfully converted audio to 16kHz PCM WAV ({output_wav.stat().st_size} bytes)")
        else:
            print(f"FFmpeg conversion warning code {sub_res.returncode}: {sub_res.stderr}")
    except Exception as conv_err:
        print(f"FFmpeg conversion error: {conv_err}")

    # 2. Transcribe converted WAV file (or input_path as fallback)
    target_path_for_whisper = output_wav if conversion_successful else input_path
    transcript_text = ""
    detected_lang = "en"
    lang_arg = None if language == "auto" else language

    try:
        res = model.transcribe(str(target_path_for_whisper), language=lang_arg, fp16=False)
        transcript_text = res.get("text", "").strip()
        detected_lang = res.get("language", "en")
    except Exception as e:
        print(f"Whisper transcription error: {e}")

    # Clean up temp files
    for p in [input_path, output_wav]:
        try:
            if p.exists():
                p.unlink()
        except Exception:
            pass

    return {
        "text": transcript_text,
        "detected_language": detected_lang,
        "language_used": language
    }
