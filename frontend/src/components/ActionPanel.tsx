export default function ActionPanel() {
  return (
    <div className="mt-8">
      <h2 className="font-bold mb-3">Actions</h2>

      <div className="space-y-2 text-sm">
        <div className="bg-zinc-900 p-3 rounded-lg">
          Reminder created
        </div>

        <div className="bg-zinc-900 p-3 rounded-lg">
          Email draft generated
        </div>
      </div>
    </div>
  );
}