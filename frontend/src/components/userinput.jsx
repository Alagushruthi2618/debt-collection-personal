import { useState, useRef, useEffect } from "react";

function UserInput({ onSend, disabled, isLoading, isComplete }) {
  const [text, setText] = useState("");
  const inputRef = useRef(null);

  // Keep focus on input after sending message
  useEffect(() => {
    if (!disabled && inputRef.current) {
      inputRef.current.focus();
    }
  }, [disabled]);

  function handleSend() {
    if (!text.trim()) return;
    onSend(text);
    setText("");
    // Focus input after sending
    setTimeout(() => {
      if (inputRef.current) {
        inputRef.current.focus();
      }
    }, 100);
  }

  function handleKeyPress(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  let placeholder = "Type your message...";
  if (isComplete) {
    placeholder = "Chat completed";
  } else if (isLoading) {
    placeholder = "Chat is thinking...";
  }

  return (
    <div className="flex gap-2 p-4 bg-white border-t border-gray-200 flex-shrink-0">
      <input
        ref={inputRef}
        type="text"
        value={text}
        disabled={disabled}
        onChange={(e) => setText(e.target.value)}
        onKeyPress={handleKeyPress}
        placeholder={placeholder}
        className="flex-1 px-4 py-3 rounded-xl border border-gray-200 bg-white text-gray-900 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed transition-all"
      />
      <button
        onClick={handleSend}
        disabled={disabled || !text.trim()}
        className="w-11 h-11 rounded-xl bg-gradient-to-r from-blue-500 to-indigo-500 text-white flex items-center justify-center cursor-pointer hover:from-blue-600 hover:to-indigo-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-sm hover:shadow-md active:scale-95"
      >
        <svg
          width="16"
          height="16"
          viewBox="0 0 16 16"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          className="transform rotate-0"
        >
          <path
            d="M2 2L14 8L2 14V2Z"
            fill="currentColor"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </button>
    </div>
  );
}

export default UserInput;
