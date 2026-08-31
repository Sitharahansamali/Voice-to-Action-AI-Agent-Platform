"use client";

import { useEffect, useState } from "react";
import { Bell, FileText, RefreshCw } from "lucide-react";
import api from "@/services/api";

export default function MemoryPanel() {
  const [reminders, setReminders] = useState<any[]>([]);
  const [notes, setNotes] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchMemory = async () => {
    setLoading(true);
    try {
      const [remRes, noteRes] = await Promise.all([
        api.get("/reminders"),
        api.get("/notes")
      ]);
      if (remRes.data && remRes.data.reminders) {
        setReminders(remRes.data.reminders);
      }
      if (noteRes.data && noteRes.data.notes) {
        setNotes(noteRes.data.notes);
      }
    } catch (e) {
      console.error("Failed to load memory data:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMemory();
  }, []);

  return (
    <div className="space-y-4 mb-6">
      <div className="flex items-center justify-between">
        <h2 className="font-bold text-sm tracking-wide text-zinc-300 uppercase">Memory & Storage</h2>
        <button
          onClick={fetchMemory}
          className="text-zinc-500 hover:text-zinc-300 transition"
          title="Refresh memory"
        >
          <RefreshCw size={14} className={loading ? "animate-spin" : ""} />
        </button>
      </div>

      {/* Reminders */}
      <div className="space-y-2">
        <div className="flex items-center space-x-1.5 text-xs text-zinc-400 font-semibold">
          <Bell size={14} className="text-blue-400" />
          <span>Active Reminders ({reminders.length})</span>
        </div>

        <div className="space-y-1.5 max-h-40 overflow-y-auto pr-1">
          {reminders.length === 0 ? (
            <p className="text-[11px] text-zinc-600 italic">No reminders saved yet.</p>
          ) : (
            reminders.map((r, i) => (
              <div key={i} className="bg-zinc-900 border border-zinc-800 p-2.5 rounded-lg text-xs">
                <p className="font-medium text-zinc-200">{r.text}</p>
                <p className="text-[10px] text-blue-400 mt-0.5">{r.due_time}</p>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Notes */}
      <div className="space-y-2 pt-2 border-t border-zinc-800/60">
        <div className="flex items-center space-x-1.5 text-xs text-zinc-400 font-semibold">
          <FileText size={14} className="text-emerald-400" />
          <span>Saved Notes ({notes.length})</span>
        </div>

        <div className="space-y-1.5 max-h-40 overflow-y-auto pr-1">
          {notes.length === 0 ? (
            <p className="text-[11px] text-zinc-600 italic">No notes saved yet.</p>
          ) : (
            notes.map((n, i) => (
              <div key={i} className="bg-zinc-900 border border-zinc-800 p-2.5 rounded-lg text-xs">
                <p className="font-medium text-zinc-200">{n.title || "Note"}</p>
                <p className="text-[11px] text-zinc-400 mt-0.5 line-clamp-2">{n.content}</p>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}