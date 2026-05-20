"use client";

import { useState } from "react";

import ChatWindow from "@/components/ChatWindow";
import ActionPanel from "@/components/ActionPanel";
import MemoryPanel from "@/components/MemoryPanel";
import StatusPanel from "@/components/StatusPanel";
import MicrophoneButton from "@/components/MicrophoneButton";

export default function HomePage() {
  const [messages, setMessages] = useState<string[]>([]);
  const [language, setLanguage] = useState<string>("en");

  return (
    <main className="h-screen bg-zinc-950 text-white">
      <div className="grid grid-cols-12 h-full">

        {/* LEFT */}
        <div className="col-span-2 border-r border-zinc-800 p-4">
          <MemoryPanel />
          <ActionPanel />
        </div>

        {/* CENTER */}
        <div className="col-span-8 flex flex-col">

          <ChatWindow messages={messages} />

          <div className="border-t border-zinc-800 p-4 flex gap-3">
              <select
                 value={language}
                 onChange={(e) => setLanguage(e.target.value)}
                 className="bg-zinc-900 border border-zinc-700 rounded-lg px-3 py-2"
               >
                 <option value="en">English</option>
                 <option value="si">Sinhala</option>
                 <option value="auto">Auto Detect</option>
              </select>
             
               <input
                 className="flex-1 bg-zinc-900 rounded-lg px-4 py-3 outline-none"
                 placeholder="Ask the AI agent..."
               />

            <MicrophoneButton 
                setMessages={setMessages}
                language={language}
            />
          </div>

        </div>

        {/* RIGHT */}
        <div className="col-span-2 border-l border-zinc-800 p-4">
          <StatusPanel />
        </div>

      </div>
    </main>
  );
}