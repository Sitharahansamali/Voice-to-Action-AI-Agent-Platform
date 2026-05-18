"use client";

import { useRef, useState } from "react";

export default function useVoiceRecorder() {
  const [recording, setRecording] = useState(false);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);

  const audioChunksRef = useRef<Blob[]>([]);

  // START RECORDING
  const startRecording = async () => {
    try {
      // Ask microphone permission
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: true,
      });

      // Create media recorder
      const mediaRecorder = new MediaRecorder(stream);

      mediaRecorderRef.current = mediaRecorder;

      // Clear previous chunks
      audioChunksRef.current = [];

      // Save audio chunks
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      // Start recording
      mediaRecorder.start();

      setRecording(true);

      console.log("Recording started...");
    } catch (error) {
      console.error("Microphone access denied:", error);
    }
  };

  // STOP RECORDING
  const stopRecording = (): Promise<Blob | null> => {
    return new Promise((resolve) => {
      const mediaRecorder = mediaRecorderRef.current;

      if (!mediaRecorder) {
        resolve(null);
        return;
      }

      mediaRecorder.onstop = () => {
        // Create audio blob
        const audioBlob = new Blob(audioChunksRef.current, {
          type: "audio/webm",
        });

        setRecording(false);

        console.log("Recording stopped");

        resolve(audioBlob);
      };

      mediaRecorder.stop();
    });
  };

  return {
    recording,
    startRecording,
    stopRecording,
  };
}