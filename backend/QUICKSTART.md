# Quick Start Guide - Backend

## 🚀 Getting Started

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

Create a `.env` file in the project root:

```bash
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Start the Server

From the project root directory:

```bash
# Option 1: Using Python
python backend/app.py

# Option 2: Using Uvicorn (recommended for development)
uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
```

The server will start on `http://localhost:8000`

### 4. Test the API

**Option A: Using the test script**

```bash
# In a new terminal
python backend/test_api.py
```

**Option B: Using curl**

```bash
# Health check
curl http://localhost:8000/health

# Initialize session
curl -X POST http://localhost:8000/api/init \
  -H "Content-Type: application/json" \
  -d '{"phone": "+919876543210"}'

# Send chat message (replace SESSION_ID with the session_id from init response)
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "SESSION_ID", "user_input": "Yes, this is Rajesh"}'
```

**Option C: Using Python requests**

```python
import requests

# Initialize
response = requests.post(
    "http://localhost:8000/api/init",
    json={"phone": "+919876543210"}
)
data = response.json()
session_id = data["session_id"]

# Chat
response = requests.post(
    "http://localhost:8000/api/chat",
    json={
        "session_id": session_id,
        "user_input": "Yes, this is Rajesh"
    }
)
print(response.json())
```

## 📋 Available Test Customers

- `+919876543210` - Rajesh Kumar (DOB: 15-03-1985)
- `+919876543211` - Priya Sharma (DOB: 22-07-1990)
- `+919876543212` - Amit Patel (DOB: 05-11-1988)

## 🔍 API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🏗️ Project Structure

```
backend/
├── app.py              # FastAPI application
├── routes/
│   └── chat.py         # Chat endpoints
├── session_store.py    # Session management
├── test_api.py         # Test script
└── README.md           # Full documentation
```

## ⚠️ Important Notes

1. **Sessions are in-memory**: Sessions are stored in a Python dictionary, so they will be lost on server restart. For production, use Redis or a database.

2. **CORS**: Currently allows all origins (`*`). Update `backend/app.py` to restrict to your frontend domain in production.

3. **Error Handling**: The API returns proper HTTP status codes:
   - `200`: Success
   - `400`: Bad request (empty input, call complete, etc.)
   - `404`: Session not found
   - `500`: Internal server error

## 🔄 Integration with Frontend

The frontend (Shruti) should:

1. Call `/api/init` with phone number to start a session
2. Store the `session_id` in browser (localStorage/sessionStorage)
3. Call `/api/chat` with `session_id` and `user_input` for each message
4. Display `messages` array in chat UI
5. Show `offered_plans` as buttons when in negotiation stage
6. Check `is_complete` to know when conversation ends
7. Check `awaiting_user` to enable/disable input

## 🐛 Troubleshooting

**Import errors?**
- Make sure you're running from the project root directory
- Check that all dependencies are installed: `pip install -r requirements.txt`

**Session not found?**
- Make sure you call `/api/init` first to create a session
- Check that you're using the correct `session_id`

**Agent not responding?**
- Check that `GEMINI_API_KEY` is set in `.env`
- Check server logs for errors
- Verify the phone number exists in `src/data.py`

