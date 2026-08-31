import os
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from app.services.speech_service import transcribe_audio_file
from app.agent.graph import run_agent_workflow
from app.mcp.client import mcp_client
from app.memory.memory import search_memory

app = FastAPI(title="Voice-to-Action AI Agent Platform API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

@app.get("/")
@app.get("/health")
async def root():
    return {
        "status": "healthy",
        "service": "Voice-to-Action AI Agent Platform",
        "version": "1.0.0"
    }

@app.post("/upload-audio")
async def upload_audio(audio: UploadFile = File(...), language: str = Form("auto")):
    try:
        content = await audio.read()
        if not content:
            raise HTTPException(status_code=400, detail="Empty audio file provided.")

        transcription_res = transcribe_audio_file(
            file_bytes=content,
            filename=audio.filename or "recording.webm",
            language=language
        )
        transcript = transcription_res["text"]

        if not transcript:
            return {
                "message": "warning",
                "error": "No speech detected in audio.",
                "transcript": "",
                "response": "I couldn't hear any speech in the audio. Please try speaking again."
            }

        agent_res = run_agent_workflow(transcript)

        return {
            "message": "success",
            "transcript": transcript,
            "detected_language": transcription_res["detected_language"],
            "intent": agent_res["intent"],
            "tool_name": agent_res["tool_name"],
            "tool_arguments": agent_res["tool_arguments"],
            "tool_result": agent_res["tool_result"],
            "response": agent_res["response"],
            "steps": agent_res["steps_log"]
        }

    except Exception as e:
        print("Upload Audio Error:", str(e))
        return {
            "message": "error",
            "error": str(e),
            "response": f"An error occurred while processing audio: {str(e)}"
        }

@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    try:
        user_message = req.message.strip()
        if not user_message:
            raise HTTPException(status_code=400, detail="Message content cannot be empty.")

        agent_res = run_agent_workflow(user_message)

        return {
            "message": "success",
            "input_text": user_message,
            "intent": agent_res["intent"],
            "tool_name": agent_res["tool_name"],
            "tool_arguments": agent_res["tool_arguments"],
            "tool_result": agent_res["tool_result"],
            "response": agent_res["response"],
            "steps": agent_res["steps_log"]
        }

    except Exception as e:
        print("Chat Endpoint Error:", str(e))
        return {
            "message": "error",
            "error": str(e),
            "response": f"An error occurred: {str(e)}"
        }

@app.get("/reminders")
async def list_reminders():
    res = mcp_client.call_tool("list_reminders", {})
    return res

@app.get("/notes")
async def list_notes():
    res = mcp_client.call_tool("get_notes", {})
    return res

@app.get("/memories")
async def list_memories(query: str = ""):
    res = search_memory(query if query else "agent", n_results=5)
    return res