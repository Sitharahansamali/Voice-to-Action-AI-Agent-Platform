interface Props {
  messages: string[];
}

export default function ChatWindow({
  messages,
}: Props) {
  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-4">

      {messages.map((message, index) => (
        <div
          key={index}
          className="bg-blue-600 p-4 rounded-xl w-fit ml-auto max-w-xl"
        >
          {message}
        </div>
      ))}

    </div>
  );
}