"use client";

import { Wrench, CheckCircle2 } from "lucide-react";

export default function ActionPanel() {
  const tools = [
    { name: "Reminder Server", tools: ["create_reminder", "list_reminders", "delete_reminder"] },
    { name: "Notes Server", tools: ["save_note", "get_notes", "delete_note"] },
    { name: "Email Server", tools: ["send_email", "list_emails"] },
    { name: "Calendar Server", tools: ["create_event", "list_events"] }
  ];

  return (
    <div className="space-y-4 pt-2 border-t border-zinc-800">
      <h2 className="font-bold text-sm tracking-wide text-zinc-300 uppercase flex items-center gap-1.5">
        <Wrench size={14} className="text-amber-400" />
        <span>MCP Tool Servers</span>
      </h2>

      <div className="space-y-3 font-mono text-xs">
        {tools.map((group, idx) => (
          <div key={idx} className="bg-zinc-900/60 border border-zinc-800/80 p-2.5 rounded-xl space-y-1.5">
            <div className="flex items-center justify-between text-[11px] font-semibold text-amber-400/90">
              <span>{group.name}</span>
              <CheckCircle2 size={12} className="text-emerald-400" />
            </div>
            <div className="flex flex-wrap gap-1">
              {group.tools.map((t, i) => (
                <span key={i} className="bg-zinc-800 text-zinc-300 px-1.5 py-0.5 rounded text-[10px]">
                  {t}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}