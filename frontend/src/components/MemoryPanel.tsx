export default function MemoryPanel() {
  return (
    <div>
      <h2 className="font-bold mb-3">Memory</h2>

      <div className="space-y-2 text-sm">
        <div className="bg-zinc-900 p-3 rounded-lg">
          Yesterday meeting summary
        </div>

        <div className="bg-zinc-900 p-3 rounded-lg">
          User prefers morning reminders
        </div>
      </div>
    </div>
  );
}