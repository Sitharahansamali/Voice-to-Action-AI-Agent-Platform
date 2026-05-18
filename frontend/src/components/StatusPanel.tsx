export default function StatusPanel() {
  return (
    <div>
      <h2 className="font-bold mb-3">System Status</h2>

      <div className="space-y-3 text-sm">

        <div className="bg-zinc-900 p-3 rounded-lg">
          Backend: Connected
        </div>

        <div className="bg-zinc-900 p-3 rounded-lg">
          Whisper: Ready
        </div>

        <div className="bg-zinc-900 p-3 rounded-lg">
          MCP Tools: Active
        </div>

      </div>
    </div>
  );
}