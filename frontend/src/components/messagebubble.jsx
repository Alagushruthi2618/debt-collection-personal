function MessageBubble({ role, text }) {
  const isUser = role === "user";
  
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} animate-fade-in mb-2`}>
      <div
        className={`max-w-[75%] px-4 py-2.5 text-sm leading-relaxed rounded-2xl break-words ${
          isUser
            ? "bg-gradient-to-r from-blue-500 to-indigo-500 text-white rounded-br-sm ml-auto shadow-sm"
            : "bg-gray-100 text-gray-800 rounded-bl-sm border border-gray-200"
        }`}
      >
        {text}
      </div>
    </div>
  );
}

export default MessageBubble;
