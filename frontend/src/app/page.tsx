"use client";

import { useState } from "react";

import ChatWindow from "@/components/ChatWindow";
import ActionPanel from "@/components/ActionPanel";
import MemoryPanel from "@/components/MemoryPanel";
import StatusPanel from "@/components/StatusPanel";
import MicrophoneButton from "@/components/MicrophoneButton";

export default function HomePage() {
  const [messages, setMessages] = useState<string[]>([]);

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
            <input
              className="flex-1 bg-zinc-900 rounded-lg px-4 py-3 outline-none"
              placeholder="Ask the AI agent..."
            />

            <MicrophoneButton setMessages={setMessages} />
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