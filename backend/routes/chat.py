# backend/routes/chat.py

"""
Chat endpoint for web-based agent.
Handles user input and invokes LangGraph agent.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.graph import app
from backend.session_store import get_session, create_session, update_session


router = APIRouter()


class ChatRequest(BaseModel):
    """Request model for /chat endpoint."""
    session_id: str
    user_input: str


class ChatResponse(BaseModel):
    """Response model for /chat endpoint."""
    messages: list[dict]
    stage: str
    awaiting_user: bool
    offered_plans: list[dict]
    is_complete: bool


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Handle user chat input.
    
    Flow:
    1. Get or create session
    2. Add user message to state
    3. Update state with user input
    4. Invoke LangGraph
    5. Return response
    """
    
    session_id = request.session_id
    user_input = request.user_input.strip()
    
    # Validate input
    if not user_input:
        raise HTTPException(status_code=400, detail="user_input cannot be empty")
    
    # Get session state
    state = get_session(session_id)
    
    # If session doesn't exist, this is an error (frontend should create session first)
    if not state:
        raise HTTPException(
            status_code=404, 
            detail=f"Session {session_id} not found. Please initialize session first."
        )
    
    # Check if call is already complete
    if state.get("is_complete"):
        raise HTTPException(
            status_code=400,
            detail="Call is already complete. Please start a new session."
        )
    
    # Check if agent is awaiting user input
    if not state.get("awaiting_user"):
        # This might happen if frontend sends input when agent isn't ready
        # We'll allow it but log a warning
        pass
    
    # Add user message to state
    state["messages"].append({
        "role": "user",
        "content": user_input
    })
    
    # Update state with user input (nodes read from last_user_input)
    state["last_user_input"] = user_input
    state["awaiting_user"] = False
    
    try:
        # Invoke LangGraph agent
        # The graph will process the input and update state
        config = {"recursion_limit": 25}
        updated_state = app.invoke(state, config)
        
        # Update session store with new state
        update_session(session_id, updated_state)
        
        # Extract response data
        messages = updated_state.get("messages", [])
        stage = updated_state.get("stage", "unknown")
        awaiting_user = updated_state.get("awaiting_user", False)
        offered_plans = updated_state.get("offered_plans", [])
        is_complete = updated_state.get("is_complete", False)
        
        return ChatResponse(
            messages=messages,
            stage=stage,
            awaiting_user=awaiting_user,
            offered_plans=offered_plans,
            is_complete=is_complete
        )
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"[ERROR] Chat endpoint error: {e}")
        print(error_trace)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat: {str(e)}"
        )


class InitRequest(BaseModel):
    """Request model for /init endpoint."""
    phone: str


@router.post("/init")
async def init_session(request: InitRequest):
    """
    Initialize a new session for a phone number.
    Returns session_id and initial state.
    """
    phone = request.phone.strip()
    
    if not phone:
        raise HTTPException(status_code=400, detail="phone cannot be empty")
    
    session_id, state = create_session(phone)
    
    if not state:
        raise HTTPException(
            status_code=404,
            detail=f"Customer with phone {phone} not found"
        )
    
    # Invoke graph to get initial greeting
    try:
        config = {"recursion_limit": 25}
        initial_state = app.invoke(state, config)
        update_session(session_id, initial_state)
        
        # Return session info
        return {
            "session_id": session_id,
            "messages": initial_state.get("messages", []),
            "stage": initial_state.get("stage", "init"),
            "awaiting_user": initial_state.get("awaiting_user", False),
            "offered_plans": initial_state.get("offered_plans", []),
            "is_complete": initial_state.get("is_complete", False)
        }
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"[ERROR] Init session error: {e}")
        print(error_trace)
        raise HTTPException(
            status_code=500,
            detail=f"Error initializing session: {str(e)}"
        )

