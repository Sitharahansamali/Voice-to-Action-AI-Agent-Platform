"use client";

import { useEffect, useState } from "react";
import api from "@/services/api";

export default function StatusPanel() {
  const [backendStatus, setBackendStatus] = useState<"checking" | "online" | "offline">("checking");

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const res = await api.get("/health");
        if (res.data.status === "healthy") {
          setBackendStatus("online");
        } else {
          setBackendStatus("offline");
        }
      } catch (err) {
        setBackendStatus("offline");
      }
    };
    checkHealth();
    const interval = setInterval(checkHealth, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="space-y-4">
      <h2 className="font-bold text-sm tracking-wide text-zinc-300 uppercase">System Status</h2>

      <div className="space-y-2 text-xs font-mono">
        <div className="bg-zinc-900 border border-zinc-800 p-3 rounded-xl flex items-center justify-between">
          <span className="text-zinc-400">FastAPI Backend</span>
          <span className={`px-2 py-0.5 rounded font-semibold ${
            backendStatus === "online" ? "bg-emerald-950 text-emerald-400 border border-emerald-800" :
            backendStatus === "offline" ? "bg-red-950 text-red-400 border border-red-800" :
            "bg-zinc-800 text-zinc-400"
          }`}>
            {backendStatus.toUpperCase()}
          </span>
        </div>

        <div className="bg-zinc-900 border border-zinc-800 p-3 rounded-xl flex items-center justify-between">
          <span className="text-zinc-400">Whisper STT</span>
          <span className="bg-emerald-950 text-emerald-400 border border-emerald-800 px-2 py-0.5 rounded font-semibold">
            READY (Base)
          </span>
        </div>

        <div className="bg-zinc-900 border border-zinc-800 p-3 rounded-xl flex items-center justify-between">
          <span className="text-zinc-400">HF Intent Detector</span>
          <span className="bg-emerald-950 text-emerald-400 border border-emerald-800 px-2 py-0.5 rounded font-semibold">
            ACTIVE (XLM-R)
          </span>
        </div>

        <div className="bg-zinc-900 border border-zinc-800 p-3 rounded-xl flex items-center justify-between">
          <span className="text-zinc-400">LangGraph Agent</span>
          <span className="bg-blue-950 text-blue-400 border border-blue-800 px-2 py-0.5 rounded font-semibold">
            COMPILED
          </span>
        </div>

        <div className="bg-zinc-900 border border-zinc-800 p-3 rounded-xl flex items-center justify-between">
          <span className="text-zinc-400">MCP Servers</span>
          <span className="bg-emerald-950 text-emerald-400 border border-emerald-800 px-2 py-0.5 rounded font-semibold">
            4 REGISTERED
          </span>
        </div>

        <div className="bg-zinc-900 border border-zinc-800 p-3 rounded-xl flex items-center justify-between">
          <span className="text-zinc-400">Database & RAG</span>
          <span className="bg-emerald-950 text-emerald-400 border border-emerald-800 px-2 py-0.5 rounded font-semibold">
            CONNECTED
          </span>
        </div>
      </div>
    </div>
  );
}