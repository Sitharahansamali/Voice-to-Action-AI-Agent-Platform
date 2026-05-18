export default function ChatWindow() {
  return (
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
      
      <div className="bg-zinc-800 p-4 rounded-xl w-fit max-w-xl">
        Hello! How can I help you?
      </div>

      <div className="bg-blue-600 p-4 rounded-xl w-fit ml-auto max-w-xl">
        Create reminder for tomorrow
      </div>

    </div>
  );
}