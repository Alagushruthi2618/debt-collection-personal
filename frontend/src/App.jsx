import { useState } from "react";
import ChatWindow from "./components/chatwindow";
import UserInput from "./components/userinput";
import { startChat, sendChatMessage } from "./api/chatapi";

function App() {
  const [phone, setPhone] = useState("");
  const [sessionId, setSessionId] = useState(null);
  const [callState, setCallState] = useState(null);
  const [loading, setLoading] = useState(false);
  const [started, setStarted] = useState(false);

  async function initChat() {
    if (!phone) return alert("Please enter your phone number");
    setLoading(true);
    try {
      const data = await startChat(phone);
      setSessionId(data.session_id);
      setCallState(data);
      setStarted(true);
    } catch (err) {
      console.error("Init error:", err);
      alert("Failed to start chat.");
    }
    setLoading(false);
  }

  async function handleSend(input) {
    if (!callState?.awaiting_user) return;
    setLoading(true);
    try {
      const data = await sendChatMessage(sessionId, input);
      setCallState(data);
    } catch (err) {
      console.error("Send error:", err);
    }
    setLoading(false);
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 p-6">
      {!started ? (
        <div className="w-full max-w-md bg-white rounded-2xl shadow-xl p-8 space-y-6 border border-gray-100">
          <h2 className="text-2xl font-semibold text-gray-800">
            Enter your phone number
          </h2>

          <input
            type="tel"
            placeholder="Enter phone number (Press Enter to continue)"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && phone && !loading) {
                e.preventDefault();
                initChat();
              }
            }}
            className="w-full px-4 py-3 border border-gray-300 rounded-xl bg-white text-gray-800 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
          />

          <button
            onClick={initChat}
            disabled={loading || !phone}
            className="w-full px-4 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl font-semibold hover:from-blue-700 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-md hover:shadow-lg"
          >
            {loading ? "Starting..." : "Start Chat"}
          </button>
        </div>
      ) : (
        <div className="w-full max-w-md h-[600px] bg-white rounded-3xl shadow-2xl flex flex-col overflow-hidden border border-gray-100">
          <div className="flex-1 min-h-0 flex flex-col">
            <ChatWindow
              messages={callState?.messages || []}
              isComplete={callState?.is_complete}
            />
          </div>

          <UserInput
            onSend={handleSend}
            disabled={callState?.is_complete || !callState?.awaiting_user || loading}
            isLoading={loading}
            isComplete={callState?.is_complete}
          />
        </div>
      )}
    </div>
  );
}

export default App;
