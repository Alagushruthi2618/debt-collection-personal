# backend/session_store.py

"""
Session management for web-based agent.
Stores session_id → CallState mapping.
"""

from typing import Optional
import uuid
from src.state import CallState, create_initial_state


# In-memory session store
# In production, this would be Redis or a database
_sessions: dict[str, CallState] = {}


def create_session(phone: str) -> tuple[str, Optional[CallState]]:
    """
    Create a new session for a given phone number.
    Returns (session_id, CallState) or (session_id, None) if customer not found.
    """
    session_id = str(uuid.uuid4())
    
    state = create_initial_state(phone)
    if not state:
        return session_id, None
    
    _sessions[session_id] = state
    return session_id, state


def get_session(session_id: str) -> Optional[CallState]:
    """Get session state by session_id."""
    return _sessions.get(session_id)


def update_session(session_id: str, state: CallState) -> None:
    """Update session state."""
    _sessions[session_id] = state


def delete_session(session_id: str) -> None:
    """Delete a session."""
    if session_id in _sessions:
        del _sessions[session_id]


def session_exists(session_id: str) -> bool:
    """Check if session exists."""
    return session_id in _sessions

