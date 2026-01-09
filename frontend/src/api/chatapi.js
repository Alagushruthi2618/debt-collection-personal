const BASE_URL = "http://localhost:8000/api";

/**
 * Start a new chat session
 * @param {string} phone - User's phone number (required)
 */
export async function startChat(phone) {
  if (!phone) {
    throw new Error("Phone number is required to start chat");
  }

  const res = await fetch(`${BASE_URL}/init`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ phone })
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Failed to start session: ${text}`);
  }

  return res.json(); // returns { session_id, messages, ... }
}

/**
 * Send a user message to the backend and get updated state
 * @param {string} sessionId - Current chat session ID
 * @param {string} userInput - User's message
 */
export async function sendChatMessage(sessionId, userInput) {
  if (!sessionId) throw new Error("Session ID is required");
  if (!userInput) throw new Error("User input cannot be empty");

  const res = await fetch(`${BASE_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, user_input: userInput })
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Failed to send message: ${text}`);
  }

  return res.json(); // returns updated state
}
