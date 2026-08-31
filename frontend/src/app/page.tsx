"use client";

import { useState } from "react";
import { Send, Bot } from "lucide-react";
import ChatWindow, { ChatMessage } from "@/components/ChatWindow";
import ActionPanel from "@/components/ActionPanel";
import MemoryPanel from "@/components/MemoryPanel";
import StatusPanel from "@/components/StatusPanel";
import MicrophoneButton from "@/components/MicrophoneButton";
import api from "@/services/api";

export default function HomePage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputText, setInputText] = useState<string>("");
  const [language, setLanguage] = useState<string>("en");
  const [loading, setLoading] = useState<boolean>(false);

  const handleSendText = async () => {
    if (!inputText.trim() || loading) return;

    const userText = inputText.trim();
    setInputText("");

    const userMsg: ChatMessage = {
      id: "user_" + Date.now(),
      sender: "user",
      text: userText,
      timestamp: new Date().toLocaleTimeString()
    };

    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    try {
      const response = await api.post("/chat", { message: userText });
      const data = response.data;

      const assistantMsg: ChatMessage = {
        id: "assistant_" + Date.now(),
        sender: "assistant",
        text: data.response || "Request completed.",
        intent: data.intent?.intent,
        confidence: data.intent?.confidence,
        tool: data.tool_name,
        steps: data.steps || [],
        timestamp: new Date().toLocaleTimeString()
      };

      setMessages((prev) => [...prev, assistantMsg]);
    } catch (error: any) {
      console.error("Chat error:", error);
      const errorMsg: ChatMessage = {
        id: "error_" + Date.now(),
        sender: "assistant",
        text: "Error communicating with backend: " + (error.message || "Failed to fetch"),
        timestamp: new Date().toLocaleTimeString()
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      e.preventDefault();
      handleSendText();
    }
  };

  const handleNewVoiceMessages = (userMsg: ChatMessage, assistantMsg: ChatMessage) => {
    setMessages((prev) => [...prev, userMsg, assistantMsg]);
  };

  return (
    <main className="h-screen bg-zinc-950 text-white flex flex-col overflow-hidden font-sans">
      {/* HEADER */}
      <header className="border-b border-zinc-800 px-6 py-3 flex items-center justify-between bg-zinc-900/50">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-blue-600/20 text-blue-400 rounded-xl border border-blue-500/30">
            <Bot size={22} />
          </div>
          <div>
            <h1 className="font-bold text-base tracking-tight text-zinc-100">Voice-to-Action AI Platform</h1>
            <p className="text-xs text-zinc-400 font-mono">Whisper STT • XLM-RoBERTa • LangGraph • MCP Servers</p>
          </div>
        </div>
      </header>

      {/* MAIN LAYOUT */}
      <div className="grid grid-cols-12 flex-1 overflow-hidden">
        {/* LEFT PANEL */}
        <div className="col-span-3 border-r border-zinc-800/80 p-4 bg-zinc-900/30 overflow-y-auto flex flex-col justify-between">
          <div>
            <MemoryPanel />
          </div>
          <ActionPanel />
        </div>

        {/* CENTER CHAT */}
        <div className="col-span-6 flex flex-col bg-zinc-950 overflow-hidden">
          <ChatWindow messages={messages} loading={loading} />

          {/* INPUT BAR */}
          <div className="border-t border-zinc-800 p-4 flex items-center gap-3 bg-zinc-900/40">
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="bg-zinc-900 border border-zinc-700 text-xs text-zinc-300 rounded-xl px-3 py-3 outline-none hover:border-zinc-500 transition cursor-pointer"
            >
              <option value="en">English</option>
              <option value="si">Sinhala</option>
              <option value="auto">Auto Detect</option>
            </select>

            <input
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={loading}
              className="flex-1 bg-zinc-900 border border-zinc-800 focus:border-blue-500 text-sm text-zinc-100 rounded-xl px-4 py-3 outline-none transition placeholder-zinc-500"
              placeholder="Speak or type a request (e.g. Remind me tomorrow at 9 AM to call John)..."
            />

            <button
              onClick={handleSendText}
              disabled={loading || !inputText.trim()}
              className="bg-blue-600 hover:bg-blue-700 disabled:opacity-40 text-white p-3 rounded-xl transition flex items-center justify-center"
              title="Send Text Message"
            >
              <Send size={20} />
            </button>

            <MicrophoneButton
              onNewMessages={handleNewVoiceMessages}
              language={language}
            />
          </div>
        </div>

        {/* RIGHT PANEL */}
        <div className="col-span-3 border-l border-zinc-800/80 p-4 bg-zinc-900/30 overflow-y-auto">
          <StatusPanel />
        </div>
      </div>
    </main>
  );
}