# Voice-to-Action AI Agent Platform

An autonomous, multi-modal **Voice-to-Action AI Agent Platform** combining Whisper speech-to-text, Hugging Face zero-shot intent detection, LangGraph agent workflows, MCP (Model Context Protocol) Client/Server architecture, and RAG vector memory.

---

## 🏗️ Architecture Overview

```
                    USER
                     │
              Voice / Text
                     │
                     ▼
              ┌─────────────┐
              │   Next.js   │
              │  Frontend   │
              └──────┬──────┘
                     │
                  HTTP/API
                     │
                     ▼
              ┌─────────────┐
              │   FastAPI   │
              │   Backend   │
              └──────┬──────┘
                     │
          ┌──────────┴──────────┐
          │                     │
          ▼                     ▼
      Whisper             Intent Detection
   Speech → Text       (XLM-RoBERTa / BART)
          │                     │
          └──────────┬──────────┘
                     ▼
              ┌─────────────┐
              │  LangGraph  │
              │    Agent    │
              └──────┬──────┘
                     │
              ┌──────┴──────┐
              │             │
              ▼             ▼
          RAG Memory    MCP Client
          (ChromaDB)        │
                            ▼
                       MCP Servers
             ┌──────────────┼──────────────┐
             │              │              │
             ▼              ▼              ▼
           Notes        Reminder         Email /
          Server         Server         Calendar
                            │
                            ▼
                    Database (MongoDB / Local DB)
```

---

## 🚀 Key Features

1. **Dual Input (Voice & Text)**: Supports direct text input and browser microphone voice recordings transcribed with OpenAI Whisper (`base` model).
2. **Hugging Face Intent Detection**: Uses `joeddav/xlm-roberta-large-xnli` zero-shot classification with confidence thresholding.
3. **LangGraph Agent Workflow**:
   - `Intent Detection` -> `RAG Memory Retrieval` -> `Planner` -> `MCP Tool Execution` -> `Response Generation`.
4. **Decoupled MCP Architecture**:
   - **MCP Client**: Discovers available tool servers and executes validated arguments.
   - **MCP Servers**: Separate modules for **Reminders**, **Notes**, **Emails**, and **Calendar**.
5. **Hybrid Persistence & RAG Memory**:
   - Stores application data in **MongoDB** (with local JSON fallback).
   - Embedded semantic memory search with **ChromaDB**.
6. **Live Visual Execution Trace**: Next.js UI visualizes agent planning, intent confidence, MCP server connections, and step execution.

---

## 🛠️ Project Structure

```
voice-to-action-ai/
├── backend/
│   ├── app/
│   │   ├── agent/
│   │   │   └── graph.py          # LangGraph state machine workflow
│   │   ├── db/
│   │   │   └── database.py       # MongoDB & Local DB persistence
│   │   ├── mcp/
│   │   │   ├── client.py         # MCP Client layer
│   │   │   └── servers/          # Reminder, Notes, Email, Calendar MCP Servers
│   │   │       ├── reminder_server.py
│   │   │       ├── notes_server.py
│   │   │       ├── email_server.py
│   │   │       └── calendar_server.py
│   │   ├── memory/
│   │   │   └── memory.py         # ChromaDB RAG vector memory
│   │   ├── services/
│   │   │   ├── intent_detector.py # Hugging Face zero-shot intent classifier
│   │   │   └── speech_service.py  # Whisper speech-to-text pipeline
│   │   └── main.py               # FastAPI application & endpoints
│   ├── tests/
│   │   └── test_pipeline.py      # Automated backend integration test suite
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── app/                  # Next.js App router page & styles
    │   ├── components/           # ActionPanel, ChatWindow, MemoryPanel, StatusPanel, MicrophoneButton
    │   ├── hooks/                # useVoiceRecorder hook
    │   └── services/             # Axios API service
    └── next.config.ts            # Next.js cross-origin configuration
```

---

## ⚙️ Environment & Setup

### 1. Backend (Python Conda Environment `voice-ai`)

Activate your Conda environment and install dependencies:

```bash
conda activate voice-ai
cd backend
pip install -r requirements.txt
```

Run the backend server:

```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### 2. Frontend (Next.js)

Navigate to `frontend/` and run the development server:

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## 🧪 Testing

Run the automated backend test suite:

```bash
cd backend
python -m unittest discover tests
```

---

## 📡 API Endpoints

- `GET /health` — Check backend status.
- `POST /upload-audio` — Upload webm/wav audio for Whisper STT and agent action processing.
- `POST /chat` — Send text requests to the LangGraph agent (`{"message": "..."}`).
- `GET /reminders` — Fetch list of saved reminders.
- `GET /notes` — Fetch list of saved notes.
- `GET /memories` — Query ChromaDB vector memory.
