"""Supabase database operations for sessions, messages, and briefs."""

from typing import Any, Optional

from supabase import create_client, Client
from src.config import SUPABASE_URL, SUPABASE_ANON_KEY


def get_supabase_client() -> Client:
    """Create a Supabase client."""
    return create_client(SUPABASE_URL, SUPABASE_ANON_KEY)


# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------

def sign_up(client: Client, email: str, password: str) -> Any:
    """Sign up a new user. Returns the auth response."""
    return client.auth.sign_up({"email": email, "password": password})


def sign_in(client: Client, email: str, password: str) -> Any:
    """Sign in an existing user. Returns the auth response."""
    return client.auth.sign_in_with_password({"email": email, "password": password})


def sign_out(client: Client) -> None:
    """Sign out the current user."""
    client.auth.sign_out()


def get_user_id(client: Client) -> Optional[str]:
    """Get the current authenticated user's ID."""
    user = client.auth.get_user()
    if user and user.user:
        return user.user.id
    return None


# ---------------------------------------------------------------------------
# Session CRUD
# ---------------------------------------------------------------------------

def create_session(client: Client, user_id: str, mode: Optional[str] = None) -> Any:
    """Create a new ideation session."""
    data = {"user_id": user_id, "mode": mode, "status": "active"}
    result = client.table("sessions").insert(data).execute()
    return result.data[0]


def get_active_sessions(client: Client, user_id: str) -> list[Any]:
    """Get all active sessions for a user, newest first."""
    result = (
        client.table("sessions")
        .select("*")
        .eq("user_id", user_id)
        .eq("status", "active")
        .order("created_at", desc=True)
        .execute()
    )
    return result.data


def get_session(client: Client, session_id: str) -> Any:
    """Get a specific session by ID."""
    result = (
        client.table("sessions")
        .select("*")
        .eq("id", session_id)
        .single()
        .execute()
    )
    return result.data


def update_session_mode(client: Client, session_id: str, mode: str) -> None:
    """Set the mode on a session once the user picks a path."""
    client.table("sessions").update({"mode": mode}).eq("id", session_id).execute()


def complete_session(client: Client, session_id: str) -> None:
    """Mark a session as completed."""
    client.table("sessions").update({"status": "completed"}).eq("id", session_id).execute()


# ---------------------------------------------------------------------------
# Message CRUD
# ---------------------------------------------------------------------------

def save_message(client: Client, session_id: str, role: str, content: str) -> Any:
    """Save a single message to the database."""
    data = {"session_id": session_id, "role": role, "content": content}
    result = client.table("messages").insert(data).execute()
    return result.data[0]


def load_messages(client: Client, session_id: str) -> list[Any]:
    """Load all messages for a session, ordered chronologically."""
    result = (
        client.table("messages")
        .select("*")
        .eq("session_id", session_id)
        .order("created_at", desc=False)
        .execute()
    )
    return result.data


# ---------------------------------------------------------------------------
# Brief CRUD
# ---------------------------------------------------------------------------

def save_brief(
    client: Client,
    session_id: str,
    problem_statement: str,
    project_title: str,
    project_card: str,
    interview_line: str,
) -> Any:
    """Save a generated project card."""
    data = {
        "session_id": session_id,
        "problem_statement": problem_statement,
        "project_title": project_title,
        "project_card": project_card,
        "interview_line": interview_line,
    }
    result = client.table("briefs").insert(data).execute()
    return result.data[0]


def get_brief(client: Client, session_id: str) -> Any:
    """Get the brief for a session, if one exists."""
    result = (
        client.table("briefs")
        .select("*")
        .eq("session_id", session_id)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    return result.data[0] if result.data else None
