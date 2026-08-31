"use client";

import { useState } from "react";
import { CheckCircle2, AlertCircle, ChevronDown, ChevronUp, Bot, User, Cpu } from "lucide-react";

export interface ExecutionStep {
  step: string;
  status: string;
  details: string;
}

export interface ChatMessage {
  id: string;
  sender: "user" | "assistant";
  text: string;
  intent?: string;
  confidence?: number;
  tool?: string;
  steps?: ExecutionStep[];
  timestamp: string;
}

interface Props {
  messages: ChatMessage[];
  loading: boolean;
}

export default function ChatWindow({ messages, loading }: Props) {
  const [expandedSteps, setExpandedSteps] = useState<Record<string, boolean>>({});

  const toggleExpand = (id: string) => {
    setExpandedSteps((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-6">
      {messages.length === 0 && (
        <div className="flex flex-col items-center justify-center h-full text-zinc-500 space-y-3">
          <Bot size={48} className="text-zinc-600 animate-pulse" />
          <p className="text-lg font-medium">Voice-to-Action AI Platform Ready</p>
          <p className="text-sm">Speak or type a command like "Remind me tomorrow at 9 AM to call John."</p>
        </div>
      )}

      {messages.map((msg) => {
        const isUser = msg.sender === "user";
        const isExpanded = expandedSteps[msg.id] ?? true;

        return (
          <div
            key={msg.id}
            className={`flex flex-col ${isUser ? "items-end" : "items-start"} space-y-2`}
          >
            <div className="flex items-center space-x-2 text-xs text-zinc-400 px-1">
              {isUser ? (
                <>
                  <span>You</span>
                  <User size={14} />
                </>
              ) : (
                <>
                  <Bot size={14} className="text-blue-400" />
                  <span className="text-blue-400 font-semibold">LangGraph AI Agent</span>
                  {msg.intent && (
                    <span className="bg-zinc-800 text-zinc-300 px-2 py-0.5 rounded text-[10px] font-mono">
                      Intent: {msg.intent} ({Math.round((msg.confidence || 0) * 100)}%)
                    </span>
                  )}
                </>
              )}
            </div>

            <div
              className={`p-4 rounded-2xl max-w-2xl text-sm leading-relaxed shadow-lg ${
                isUser
                  ? "bg-blue-600 text-white rounded-tr-none"
                  : "bg-zinc-900 border border-zinc-800 text-zinc-100 rounded-tl-none"
              }`}
            >
              <p className="whitespace-pre-wrap">{msg.text}</p>
            </div>

            {/* Workflow Execution Trace Panel */}
            {!isUser && msg.steps && msg.steps.length > 0 && (
              <div className="w-full max-w-2xl bg-zinc-900/80 border border-zinc-800/80 rounded-xl overflow-hidden text-xs">
                <button
                  onClick={() => toggleExpand(msg.id)}
                  className="w-full flex items-center justify-between p-2.5 bg-zinc-900 hover:bg-zinc-800/70 text-zinc-400 font-mono transition"
                >
                  <span className="flex items-center gap-2">
                    <Cpu size={14} className="text-emerald-400" />
                    Agent Workflow Trace ({msg.steps.length} Steps)
                  </span>
                  {isExpanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                </button>

                {isExpanded && (
                  <div className="p-3 space-y-2 border-t border-zinc-800/60 bg-zinc-950/60 font-mono">
                    {msg.steps.map((st, idx) => (
                      <div key={idx} className="flex items-start gap-2.5 text-zinc-300">
                        {st.status === "failed" ? (
                          <AlertCircle size={14} className="text-red-400 mt-0.5 flex-shrink-0" />
                        ) : (
                          <CheckCircle2 size={14} className="text-emerald-400 mt-0.5 flex-shrink-0" />
                        )}
                        <div className="flex-1">
                          <span className="font-semibold text-zinc-200">{st.step}: </span>
                          <span className="text-zinc-400">{st.details}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        );
      })}

      {loading && (
        <div className="flex items-center space-x-3 text-zinc-400 text-sm">
          <div className="w-3 h-3 bg-blue-500 rounded-full animate-ping" />
          <span>Processing with LangGraph Agent & MCP Servers...</span>
        </div>
      )}
    </div>
  );
}