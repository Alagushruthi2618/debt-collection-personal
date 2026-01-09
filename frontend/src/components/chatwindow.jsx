import MessageBubble from "./messagebubble";

function ChatWindow({ messages, isComplete }) {
  return (
    <div className="flex flex-col h-full">
      {/* Header with avatar and online status */}
      <div className="px-5 py-4 bg-gradient-to-r from-blue-600 to-indigo-600 text-white flex items-center gap-3">
        <div className="relative">
          <div className="w-10 h-10 rounded-full bg-blue-500 flex items-center justify-center text-white font-bold text-lg">
            α
          </div>
          <div className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-green-400 rounded-full border-2 border-white"></div>
        </div>
        <div className="flex flex-col">
          <div className="font-semibold text-sm">ABC Finance User</div>
          <div className="text-xs opacity-90">ABC Finance Assistant</div>
        </div>
      </div>

      {/* Message area */}
      <div className="flex-1 overflow-y-auto p-4 bg-white flex flex-col gap-2.5 min-h-0">
        {messages.length === 0 ? (
          <div className="flex-1 flex items-center justify-center text-muted-foreground text-sm">
            Start a conversation...
          </div>
        ) : (
          messages.map((m, i) => (
            <MessageBubble key={i} role={m.role} text={m.content} />
          ))
        )}

        {isComplete && (
          <div className="px-4 py-3 bg-green-50 text-green-700 text-center font-semibold border border-green-200 text-sm rounded-lg mt-2">
            ✅ Call Completed
          </div>
        )}
      </div>
    </div>
  );
}

export default ChatWindow;
