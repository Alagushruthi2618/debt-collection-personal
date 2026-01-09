# How to Run the Web App

The web app consists of two parts:
1. **Backend** (FastAPI) - Port 8000
2. **Frontend** (React + Vite) - Port 5173 (default)

## Quick Start

### Step 1: Start the Backend Server

Open a terminal and run:

```bash
# Option 1: Direct Python
python backend/app.py

# Option 2: Using Uvicorn (recommended for development)
uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
```

The `--reload` flag enables auto-reload on code changes.

**Verify backend is running:**
- Visit: http://localhost:8000/health
- Should return: `{"status": "healthy"}`

### Step 2: Start the Frontend

Open a **NEW terminal** (keep backend running) and run:

```bash
cd frontend
npm install  # Only needed first time or after dependency changes
npm run dev
```

The frontend will start on http://localhost:5173

### Step 3: Access the Web App

Open your browser and go to: **http://localhost:5173**

## Environment Variables

Make sure your `.env` file in the project root has:
```
GEMINI_API_KEY=your_api_key_here
```

## Testing the API Directly

You can test the backend API endpoints:

```bash
# Health check
curl http://localhost:8000/health

# Initialize a session
curl -X POST http://localhost:8000/api/init \
  -H "Content-Type: application/json" \
  -d '{"phone": "+919876543210"}'

# Send a chat message (replace SESSION_ID from init response)
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "YOUR_SESSION_ID", "user_input": "Yes, this is Rajesh"}'
```

## Test Phone Numbers

Use these test phone numbers in the web app:
- `+919876543210` - Rajesh Kumar (DOB: 15-03-1985)
- `+919876543211` - Priya Sharma (DOB: 22-07-1990)
- `+919876543212` - Amit Patel (DOB: 05-11-1988)

## Troubleshooting

### Backend Issues

1. **Port 8000 already in use:**
   ```bash
   # Change port
   uvicorn backend.app:app --host 0.0.0.0 --port 8001 --reload
   ```
   Then update `frontend/src/api/chatapi.js` to use `http://localhost:8001`

2. **Module not found errors:**
   ```bash
   pip install -r requirements.txt
   ```

### Frontend Issues

1. **npm install errors:**
   - Delete `node_modules` and `package-lock.json`
   - Run `npm install` again

2. **Connection refused to backend:**
   - Make sure backend is running on port 8000
   - Check `frontend/src/api/chatapi.js` has correct `BASE_URL`

3. **CORS errors:**
   - Backend already has CORS enabled for all origins
   - If issues persist, check backend logs

## Production Deployment

For production:
1. Build frontend: `cd frontend && npm run build`
2. Serve backend with a production ASGI server (e.g., gunicorn with uvicorn workers)
3. Serve frontend static files or use a CDN
4. Update CORS origins in `backend/app.py` to specific domains

