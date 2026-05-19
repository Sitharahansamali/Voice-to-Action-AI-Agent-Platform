
"use client";

import { Mic, Square } from "lucide-react";

import useVoiceRecorder from "@/hooks/useVoiceRecorder";

import api from "@/services/api";

interface Props {
  setMessages: React.Dispatch<
    React.SetStateAction<string[]>
  >;
}

export default function MicrophoneButton({ setMessages }: Props) {
  const {
    recording,
    startRecording,
    stopRecording,
  } = useVoiceRecorder();

  // Handle button click
  const handleRecording = async () => {
    if (!recording) {
      // START
      await startRecording();
    } else {
      // STOP
      const audioBlob = await stopRecording();

      if (audioBlob) {
      const formData = new FormData();
    
      formData.append(
        "audio",
        audioBlob,
        "recording.webm"
      );
    
      try {
        const response = await api.post(
          "/upload-audio",
          formData
        );
    
        console.log(response.data);

        setMessages((prev) => [
          ...prev,
          response.data.transcript,
    ]);

      } catch (error) {
        console.error("Upload failed:", error);
      }
}    

      // TEMP: play recorded audio
      if (audioBlob) {
        const audioUrl = URL.createObjectURL(audioBlob);

        const audio = new Audio(audioUrl);

        audio.play();
      }
    }
  };

  return (
    <button
      onClick={handleRecording}
      className={`
        p-3 rounded-xl transition
        ${
          recording
            ? "bg-red-600 hover:bg-red-700"
            : "bg-blue-600 hover:bg-blue-700"
        }
      `}
    >
      {recording ? <Square size={22} /> : <Mic size={22} />}
    </button>
  );
}
