"use client";

import { useState } from "react";
import { Mic, Square, Loader2 } from "lucide-react";
import useVoiceRecorder from "@/hooks/useVoiceRecorder";
import api from "@/services/api";
import { ChatMessage } from "./ChatWindow";

interface Props {
  onNewMessages: (userMsg: ChatMessage, assistantMsg: ChatMessage) => void;
  language: string;
}

export default function MicrophoneButton({ onNewMessages, language }: Props) {
  const { recording, startRecording, stopRecording } = useVoiceRecorder();
  const [uploading, setUploading] = useState(false);

  const handleRecording = async () => {
    if (!recording) {
      await startRecording();
    } else {
      setUploading(true);
      const audioBlob = await stopRecording();

      if (!audioBlob || audioBlob.size === 0) {
        const userMsg: ChatMessage = {
          id: "user_" + Date.now(),
          sender: "user",
          text: "[Voice Recording]",
          timestamp: new Date().toLocaleTimeString()
        };
        const assistantMsg: ChatMessage = {
          id: "assistant_" + Date.now(),
          sender: "assistant",
          text: "Audio recording was empty. Please hold the microphone button while speaking.",
          timestamp: new Date().toLocaleTimeString()
        };
        onNewMessages(userMsg, assistantMsg);
        setUploading(false);
        return;
      }

      const formData = new FormData();
      const ext = audioBlob.type.includes("mp4") ? "mp4" : audioBlob.type.includes("ogg") ? "ogg" : "webm";
      formData.append("audio", audioBlob, `recording.${ext}`);
      formData.append("language", language);

      try {
        const response = await api.post("/upload-audio", formData, {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        });
        const data = response.data;

        const userMsg: ChatMessage = {
          id: "user_" + Date.now(),
          sender: "user",
          text: data.transcript || "[Voice Recording]",
          timestamp: new Date().toLocaleTimeString()
        };

        const assistantMsg: ChatMessage = {
          id: "assistant_" + Date.now(),
          sender: "assistant",
          text: data.response || data.error || (data.message === "warning" ? "No speech detected in audio." : "Processed voice input."),
          intent: data.intent?.intent,
          confidence: data.intent?.confidence,
          tool: data.tool_name,
          steps: data.steps || [],
          timestamp: new Date().toLocaleTimeString()
        };

        onNewMessages(userMsg, assistantMsg);

      } catch (error: any) {
        console.error("Audio upload failed:", error);
        const userMsg: ChatMessage = {
          id: "user_" + Date.now(),
          sender: "user",
          text: "[Voice Recording]",
          timestamp: new Date().toLocaleTimeString()
        };
        const assistantMsg: ChatMessage = {
          id: "assistant_" + Date.now(),
          sender: "assistant",
          text: "Failed to upload audio to backend. Ensure FastAPI server is running on http://127.0.0.1:8000.",
          timestamp: new Date().toLocaleTimeString()
        };
        onNewMessages(userMsg, assistantMsg);
      } finally {
        setUploading(false);
      }
    }
  };

  return (
    <button
      onClick={handleRecording}
      disabled={uploading}
      className={`p-3 rounded-xl transition flex items-center justify-center ${
        uploading
          ? "bg-amber-600 text-white cursor-not-allowed"
          : recording
          ? "bg-red-600 hover:bg-red-700 text-white animate-pulse"
          : "bg-blue-600 hover:bg-blue-700 text-white"
      }`}
      title={recording ? "Stop Recording" : "Start Voice Input"}
    >
      {uploading ? (
        <Loader2 size={22} className="animate-spin" />
      ) : recording ? (
        <Square size={22} />
      ) : (
        <Mic size={22} />
      )}
    </button>
  );
}
