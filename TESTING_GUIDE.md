# Testing Guide - Debt Collection Web Agent

This guide covers how to test both the backend API and the frontend web application.

## Prerequisites

1. **Python 3.8+** installed
2. **Node.js and npm** installed
3. **Gemini API Key** - Get one from [Google AI Studio](https://makersuite.google.com/app/apikey)

## Quick Start Testing

### Step 1: Set Up Environment Variables

Create a `.env` file in the project root:

```bash
GEMINI_API_KEY=your_gemini_api_key_here
```

### Step 2: Start the Backend Server

Open a terminal in the project root:

```bash
# Install Python dependencies (if not already done)
pip install -r requirements.txt

# Start the backend server
python backend/app.py
```

Or using uvicorn:
```bash
uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
```

The backend will run on `http://localhost:8000`

### Step 3: Start the Frontend

Open a **new terminal** in the project root:

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies (if not already done)
npm install

# Start the development server
npm run dev
```

The frontend will run on `http://localhost:5173` (or another port if 5173 is busy)

### Step 4: Test in Browser

1. Open your browser and go to `http://localhost:5173`
2. Enter a test phone number: `+919876543210`
3. Click "Start Chat"
4. Start chatting!

## Testing Scenarios

### Test Customer Phone Numbers

Use these phone numbers for testing (they have pre-configured data):

- `+919876543210` - Rajesh Kumar (DOB: 15-03-1985)
- `+919876543211` - Priya Sharma (DOB: 22-07-1990)
- `+919876543212` - Amit Patel (DOB: 05-11-1988)

### Scenario 1: Happy Path (Payment Plan)

1. Start chat with `+919876543210`
2. Reply to greeting: "Yes, this is Rajesh"
3. Enter DOB: "15-03-1985"
4. When asked about payment: "I want a payment plan" or "I'm willing to pay"
5. Select a payment plan option
6. Complete the conversation

**Expected**: Agent should offer payment plans and allow selection.

### Scenario 2: Already Paid

1. Start chat with `+919876543210`
2. Reply: "Yes"
3. Enter DOB: "15-03-1985"
4. When asked about payment: "I have already made the payment" or "I already paid"

**Expected**: Agent should acknowledge the payment and mention verification, NOT create a dispute ticket.

### Scenario 3: Future Payment Commitment

1. Start chat with `+919876543210`
2. Reply: "Yes"
3. Enter DOB: "15-03-1985"
4. When asked about payment: "My salary is due tomorrow, so I can only make the payment after tomorrow"

**Expected**: Agent should classify as "willing" and acknowledge the future payment timeline, NOT say "already paid".

### Scenario 4: Dispute

1. Start chat with `+919876543210`
2. Reply: "Yes"
3. Enter DOB: "15-03-1985"
4. When asked about payment: "This is not my debt" or "I never took this loan"

**Expected**: Agent should create a dispute ticket and provide a reference number.

### Scenario 5: Callback Request

1. Start chat with `+919876543210`
2. Reply: "Yes"
3. Enter DOB: "15-03-1985"
4. When asked about payment: "I'm busy right now, can you call me later?" or "No, I am currently out of town"

**Expected**: Agent should acknowledge and confirm callback.

### Scenario 6: Unable to Pay

1. Start chat with `+919876543210`
2. Reply: "Yes"
3. Enter DOB: "15-03-1985"
4. When asked about payment: "I lost my job" or "I can't afford to pay"

**Expected**: Agent should show empathy and mention reviewing options.

### Scenario 7: Negative Response to Greeting

1. Start chat with `+919876543210`
2. When asked "Am I speaking with Rajesh Kumar?": Reply "No" or "Wrong person"

**Expected**: Agent should politely end the call, NOT proceed to verification.

## Backend API Testing

### Option 1: Using the Test Script

```bash
# Make sure backend is running first
python backend/test_api.py
```

### Option 2: Using curl

```bash
# Health check
curl http://localhost:8000/health

# Initialize session
curl -X POST http://localhost:8000/api/init \
  -H "Content-Type: application/json" \
  -d '{"phone": "+919876543210"}'

# Send chat message (replace SESSION_ID)
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "SESSION_ID", "user_input": "Yes, this is Rajesh"}'
```

### Option 3: Using Python Requests

```python
import requests

BASE_URL = "http://localhost:8000"

# Initialize
response = requests.post(
    f"{BASE_URL}/api/init",
    json={"phone": "+919876543210"}
)
data = response.json()
session_id = data["session_id"]
print(f"Session ID: {session_id}")

# Chat
response = requests.post(
    f"{BASE_URL}/api/chat",
    json={
        "session_id": session_id,
        "user_input": "Yes, this is Rajesh"
    }
)
print(response.json())
```

### Option 4: Using Swagger UI

1. Start the backend server
2. Open browser to `http://localhost:8000/docs`
3. Use the interactive API documentation to test endpoints

## Testing Specific Fixes

### Test 1: Input Focus Retention

1. Start a chat
2. Type a message and press Enter
3. **Expected**: Cursor should stay in the input box, ready for next message
4. Type another message without clicking
5. **Expected**: Should work without clicking the input box

### Test 2: No Duplicate Messages

1. Start a chat and complete the flow
2. **Expected**: Each assistant response should appear only once
3. Check that "already paid" responses don't appear twice

### Test 3: Correct Intent Classification

Test these specific phrases:

- "I have already made the payment" → Should be "paid"
- "My salary is due tomorrow, so I can only make the payment after tomorrow" → Should be "willing" (NOT "paid")
- "I can pay after next week" → Should be "willing"
- "I already paid yesterday" → Should be "paid"
- "No, I am currently out of town" → Should be "callback"

### Test 4: Greeting "No" Response

1. Start chat
2. When asked "Am I speaking with [Name]?", reply "No"
3. **Expected**: Call should end politely, NOT proceed to verification

## Debugging Tips

### Check Backend Logs

The backend prints detailed logs:
- `[PAYMENT_CHECK]` - Intent classification
- `[INTENT]` - Classification results
- `[RESPONSE_GEN]` - Response generation
- `[CLOSING]` - Closing message generation

### Check Browser Console

Open browser DevTools (F12) and check:
- Network tab for API calls
- Console tab for errors
- Check that API calls are successful (200 status)

### Common Issues

1. **"Session not found"**
   - Make sure you initialized the session first
   - Check that session_id is being stored correctly

2. **"GEMINI_API_KEY not set"**
   - Check that `.env` file exists in project root
   - Verify the API key is correct

3. **Frontend not connecting**
   - Check that backend is running on port 8000
   - Check `frontend/src/api/chatapi.js` for correct BASE_URL

4. **Intent misclassification**
   - Check backend logs for `[INTENT]` messages
   - Verify the user input is being passed correctly

## Automated Testing

Run the test scenarios:

```bash
# From project root
python tests/test_scenarios.py
```

## API Documentation

Once backend is running:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Next Steps

After testing:
1. Verify all scenarios work correctly
2. Check that responses are contextual (not template-based)
3. Verify no duplicate messages appear
4. Test edge cases (empty input, special characters, etc.)

