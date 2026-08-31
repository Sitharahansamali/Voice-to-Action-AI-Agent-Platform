"use client";

import { useRef, useState } from "react";

export default function useVoiceRecorder() {
  const [recording, setRecording] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  const getSupportedMimeType = () => {
    const types = [
      "audio/webm;codecs=opus",
      "audio/webm",
      "audio/ogg;codecs=opus",
      "audio/mp4",
      "audio/wav"
    ];
    for (const type of types) {
      if (typeof MediaRecorder !== "undefined" && MediaRecorder.isTypeSupported(type)) {
        return type;
      }
    }
    return "";
  };

  // START RECORDING
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: true,
      });

      const mimeType = getSupportedMimeType();
      const options = mimeType ? { mimeType } : undefined;
      const mediaRecorder = new MediaRecorder(stream, options);

      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data && event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.start(200); // Collect data chunks every 200ms
      setRecording(true);
      console.log("Recording started with mimeType:", mimeType || "default");
    } catch (error) {
      console.error("Microphone access or recorder initialization error:", error);
      setRecording(false);
    }
  };

  // STOP RECORDING
  const stopRecording = (): Promise<Blob | null> => {
    return new Promise((resolve) => {
      const mediaRecorder = mediaRecorderRef.current;

      if (!mediaRecorder || mediaRecorder.state === "inactive") {
        setRecording(false);
        resolve(null);
        return;
      }

      mediaRecorder.onstop = () => {
        const mimeType = mediaRecorder.mimeType || "audio/webm";
        const audioBlob = new Blob(audioChunksRef.current, { type: mimeType });

        // Stop all tracks on stream
        if (mediaRecorder.stream) {
          mediaRecorder.stream.getTracks().forEach((track) => track.stop());
        }

        setRecording(false);
        console.log("Recording stopped. Blob size:", audioBlob.size, "type:", mimeType);
        resolve(audioBlob.size > 0 ? audioBlob : null);
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