"""Streamlit app — Project Ideation Tool."""

import streamlit as st
from pydantic_ai.messages import ModelRequest, ModelResponse, UserPromptPart, TextPart

from src.database import (
    get_supabase_client,
    sign_up,
    sign_in,
    sign_out,
    get_user_id,
    create_session,
    get_active_sessions,
    get_session,
    update_session_mode,
    delete_session,
    save_message,
    load_messages,
)
from src.agent import agent, SessionContext

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Project Ideator",
    page_icon="🎯",
    layout="centered",
)

# Custom CSS — larger chat text
st.markdown(
    """
    <style>
    .stChatMessage p, .stChatMessage li {
        font-size: 1.1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Supabase client (cached per session)
# ---------------------------------------------------------------------------


def get_client():
    """Get or create the Supabase client in session state."""
    if "supabase" not in st.session_state:
        st.session_state.supabase = get_supabase_client()
    return st.session_state.supabase


# ---------------------------------------------------------------------------
# Auth UI
# ---------------------------------------------------------------------------


def auth_page():
    """Render the login / signup page."""
    st.title("🎯 Project Ideator")
    st.caption("Find a portfolio project idea worth building.")

    tab_login, tab_signup = st.tabs(["Log in", "Sign up"])

    with tab_login:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Log in")

            if submitted and email and password:
                try:
                    client = get_client()
                    response = sign_in(client, email, password)
                    st.session_state.auth = response
                    st.session_state.user_id = response.user.id
                except Exception as e:
                    st.error(f"Login failed: {e}")

        # Rerun outside the try/except — st.rerun() raises an exception
        # internally and the except block was swallowing it
        if "user_id" in st.session_state:
            st.rerun()

    with tab_signup:
        with st.form("signup_form"):
            email = st.text_input("Email", key="signup_email")
            password = st.text_input("Password", type="password", key="signup_pw")
            submitted = st.form_submit_button("Create account")

            if submitted and email and password:
                try:
                    client = get_client()
                    response = sign_up(client, email, password)
                    if response.user:
                        st.success(
                            "Account created! Check your email to confirm, then log in."
                        )
                    else:
                        st.error("Signup failed — try a different email.")
                except Exception as e:
                    st.error(f"Signup failed: {e}")


# ---------------------------------------------------------------------------
# Session picker
# ---------------------------------------------------------------------------


def session_picker():
    """Let the user resume an existing session or start a new one."""
    client = get_client()
    user_id = st.session_state.user_id

    active_sessions = get_active_sessions(client, user_id)

    st.sidebar.title("Sessions")

    if st.sidebar.button("➕ New session", use_container_width=True):
        new = create_session(client, user_id)
        st.session_state.session_id = new["id"]
        st.session_state.messages = []
        st.session_state.pydantic_history = []
        st.rerun()

    if active_sessions:
        st.sidebar.markdown("---")
        for s in active_sessions:
            col_btn, col_del = st.sidebar.columns([4, 1])

            # Build label
            label = f"{s['created_at'][:10]}"
            if s["mode"]:
                label += f" — {s['mode']}"

            # Highlight current session
            current = st.session_state.get("session_id") == s["id"]
            if current:
                label = f"▶ {label}"

            with col_btn:
                if st.button(label, key=s["id"], use_container_width=True):
                    load_session(s["id"])
                    st.rerun()

            with col_del:
                if st.button("🗑️", key=f"del_{s['id']}"):
                    delete_session(client, s["id"])
                    # If we deleted the current session, clear it
                    if st.session_state.get("session_id") == s["id"]:
                        st.session_state.pop("session_id", None)
                        st.session_state.pop("messages", None)
                        st.session_state.pop("pydantic_history", None)
                    st.rerun()

    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Log out", use_container_width=True):
        try:
            sign_out(client)
        except Exception:
            pass
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()


def load_session(session_id: str):
    """Load a session's message history from Supabase and rebuild state."""
    client = get_client()
    st.session_state.session_id = session_id

    db_messages = load_messages(client, session_id)

    # Rebuild display messages (for Streamlit chat UI)
    st.session_state.messages = [
        {"role": m["role"], "content": m["content"]} for m in db_messages
    ]

    # Rebuild PydanticAI message history for LLM context
    st.session_state.pydantic_history = rebuild_pydantic_history(db_messages)


def rebuild_pydantic_history(db_messages: list[dict]) -> list:
    """
    Convert stored messages (role/content dicts) into PydanticAI
    ModelRequest/ModelResponse objects for message_history injection.
    """
    history = []
    for m in db_messages:
        if m["role"] == "user":
            history.append(ModelRequest(parts=[UserPromptPart(content=m["content"])]))
        elif m["role"] == "assistant":
            history.append(ModelResponse(parts=[TextPart(content=m["content"])]))
    return history


# ---------------------------------------------------------------------------
# Chat UI
# ---------------------------------------------------------------------------


def chat_page():
    """Main chat interface."""
    st.title("🎯 Project Ideator")

    # If no session selected, try to load the most recent one
    if "session_id" not in st.session_state:
        client = get_client()
        active_sessions = get_active_sessions(client, st.session_state.user_id)
        if active_sessions:
            # Resume the most recent session
            load_session(active_sessions[0]["id"])
        else:
            # First time user — create their first session
            new = create_session(client, st.session_state.user_id)
            st.session_state.session_id = new["id"]
            st.session_state.messages = []
            st.session_state.pydantic_history = []

    # Initialize messages list if needed
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "pydantic_history" not in st.session_state:
        st.session_state.pydantic_history = []

    # Display conversation history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # If conversation is empty, get the bot's opening message
    if not st.session_state.messages:
        get_bot_response(None)

    # Chat input
    if user_input := st.chat_input("Type your response..."):
        # Display user message
        with st.chat_message("user"):
            st.markdown(user_input)

        # Save to state + DB
        st.session_state.messages.append({"role": "user", "content": user_input})
        client = get_client()
        save_message(client, st.session_state.session_id, "user", user_input)

        # Get bot response
        get_bot_response(user_input)


def get_bot_response(user_input: str | None):
    """
    Run the PydanticAI agent and display + persist the response.

    If user_input is None, this is the opening message (no user prompt yet).
    The agent will generate its opening question based on the system prompt.
    """
    client = get_client()
    session_id = st.session_state.session_id

    # Get session info for context
    session = get_session(client, session_id)
    ctx = SessionContext(
        session_id=session_id,
        mode=session.get("mode") if session else None,
    )

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Build the prompt
                if user_input is None:
                    # Opening message — ask the agent to introduce itself
                    prompt = (
                        "Start a new conversation. This is your first message to the "
                        "user. Follow Step 0 from your instructions."
                    )
                else:
                    prompt = user_input

                # Run the agent with message history
                result = agent.run_sync(
                    prompt,
                    message_history=st.session_state.pydantic_history or None,
                    deps=ctx,
                )

                # Extract the text response
                response_text = result.output

                # Update PydanticAI message history
                st.session_state.pydantic_history = list(result.all_messages())

                # Display
                st.markdown(response_text)

                # Save to state + DB
                st.session_state.messages.append(
                    {"role": "assistant", "content": response_text}
                )
                save_message(client, session_id, "assistant", response_text)

                # Check if the response indicates a mode selection
                detect_and_save_mode(response_text, session_id, client)

            except Exception as e:
                st.error(f"Something went wrong: {e}")
                st.caption(
                    "This might be a rate limit from Groq. Wait a moment and try again."
                )


def detect_and_save_mode(response_text: str, session_id: str, client):
    """
    Detect mode from conversation context and save to session.
    This is a simple heuristic — the agent's first real response after
    the user picks a path indicates the mode.
    """
    session = get_session(client, session_id)
    if session and session.get("mode") is None and len(st.session_state.messages) >= 3:
        # Check the user's first substantive reply for mode signal
        user_msgs = [m for m in st.session_state.messages if m["role"] == "user"]
        if user_msgs:
            first_reply = user_msgs[0]["content"].lower()
            if any(
                w in first_reply
                for w in ["problem", "personal", "solve", "pain", "annoying"]
            ):
                update_session_mode(client, session_id, "personal")
            elif any(
                w in first_reply
                for w in ["job", "domain", "career", "industry", "role"]
            ):
                update_session_mode(client, session_id, "domain")
            elif any(w in first_reply for w in ["both"]):
                update_session_mode(client, session_id, "both")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    """App entry point — routes between auth and chat."""
    if "user_id" not in st.session_state:
        auth_page()
    else:
        session_picker()
        chat_page()


if __name__ == "__main__":
    main()
