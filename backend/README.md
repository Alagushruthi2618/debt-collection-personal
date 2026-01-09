# Backend - Debt Collection Web Agent

This is the backend implementation for the web-based debt collection agent. It provides a FastAPI REST API that wraps the existing LangGraph agent.

## Architecture

```
backend/
├── app.py                # FastAPI application entry point
├── routes/
│   └── chat.py           # /chat and /init endpoints
├── session_store.py      # Session management (session_id → CallState)
└── requirements.txt      # Python dependencies
```

## Responsibilities

### ✅ What Backend Does

1. **Session Management**
   - Generate unique `session_id` for each conversation
   - Store `CallState` per session (in-memory, can be upgraded to Redis/DB)
   - Maintain session lifecycle

2. **LangGraph Invocation**
   - Call `create_initial_state(phone)` to initialize
   - Call `app.invoke(state)` to process user input
   - Never mutate state in place (always use returned state)

3. **State Updates**
   - Write to state: `last_user_input`, `awaiting_user`, `verification_attempts`, `is_verified`, `stage`, `is_complete`
   - Read from state: `messages`, `stage`, `awaiting_user`, `offered_plans`, `is_complete`

4. **API Contract**
   - Accept user input via POST `/api/chat`
   - Return standardized response with messages, stage, flags, and plans

### ❌ What Backend Does NOT Do

- ❌ UI logic
- ❌ Payment/negotiation business logic (handled by nodes)
- ❌ Direct LLM calls (except via nodes)
- ❌ State routing decisions (handled by `should_continue` in graph.py)

## API Endpoints

### 1. Initialize Session

**POST** `/api/init`

Initialize a new conversation session for a customer.

**Request:**
```json
{
  "phone": "+919876543210"
}
```

**Response:**
```json
{
  "session_id": "abc123-uuid",
  "messages": [
    {
      "role": "assistant",
      "content": "Hello Rajesh, good day. This is a call from ABC Finance..."
    }
  ],
  "stage": "greeting",
  "awaiting_user": true,
  "offered_plans": [],
  "is_complete": false
}
```

### 2. Chat Endpoint

**POST** `/api/chat`

Send user input and get agent response.

**Request:**
```json
{
  "session_id": "abc123-uuid",
  "user_input": "Yes, this is Rajesh"
}
```

**Response:**
```json
{
  "messages": [
    {
      "role": "assistant",
      "content": "Hello Rajesh..."
    },
    {
      "role": "user",
      "content": "Yes, this is Rajesh"
    },
    {
      "role": "assistant",
      "content": "Thank you for confirming..."
    }
  ],
  "stage": "verification",
  "awaiting_user": true,
  "offered_plans": [],
  "is_complete": false
}
```

**Response (Negotiation Stage):**
```json
{
  "messages": [...],
  "stage": "negotiation",
  "awaiting_user": true,
  "offered_plans": [
    {
      "name": "3-Month Installment",
      "description": "Pay ₹15,000 per month for 3 months"
    },
    {
      "name": "6-Month Installment",
      "description": "Pay ₹7,500 per month for 6 months"
    }
  ],
  "is_complete": false
}
```

### 3. Health Check

**GET** `/health`

Returns `{"status": "healthy"}`

## Setup

1. **Install Dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set Environment Variables:**
```bash
# .env file
GEMINI_API_KEY=your_api_key_here
```

3. **Run the Server:**
```bash
# Option 1: Direct
python backend/app.py

# Option 2: Uvicorn
uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
```

4. **Test the API:**
```bash
# Health check
curl http://localhost:8000/health

# Initialize session
curl -X POST http://localhost:8000/api/init \
  -H "Content-Type: application/json" \
  -d '{"phone": "+919876543210"}'

# Send chat message
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "your-session-id", "user_input": "Hello"}'
```

## Session Management

Currently, sessions are stored in-memory using a Python dictionary. This means:
- ✅ Fast and simple for development
- ❌ Sessions are lost on server restart
- ❌ Not suitable for production with multiple servers

**For Production:**
- Use Redis for session storage
- Add session expiration (e.g., 24 hours)
- Add session cleanup job

## State Flow

1. **Initialization:**
   - Frontend calls `/api/init` with phone number
   - Backend creates `CallState` via `create_initial_state(phone)`
   - Backend invokes graph to get initial greeting
   - Returns `session_id` and initial messages

2. **User Input:**
   - Frontend calls `/api/chat` with `session_id` and `user_input`
   - Backend:
     - Retrieves state from session store
     - Adds user message to `messages`
     - Sets `last_user_input = user_input`
     - Sets `awaiting_user = False`
     - Invokes `app.invoke(state)`
     - Updates session store
     - Returns updated state

3. **Agent Processing:**
   - LangGraph nodes process the state
   - Nodes may set `awaiting_user = True` when waiting for input
   - Nodes may set `is_complete = True` when conversation ends
   - Nodes may populate `offered_plans` during negotiation

## Error Handling

- **404**: Session not found
- **400**: Invalid input (empty user_input, call already complete)
- **500**: Internal server error (LangGraph failure, etc.)

## Testing

Test with the available mock customers:
- `+919876543210` - Rajesh Kumar (DOB: 15-03-1985)
- `+919876543211` - Priya Sharma (DOB: 22-07-1990)
- `+919876543212` - Amit Patel (DOB: 05-11-1988)

## Next Steps

1. ✅ Backend structure created
2. ⏳ Frontend integration (Shruti)
3. ⏳ Add Redis for session storage (production)
4. ⏳ Add logging and monitoring
5. ⏳ Add rate limiting
6. ⏳ Add authentication (if needed)

