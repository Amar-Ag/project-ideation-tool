"""Application configuration from environment variables."""

import os
from dotenv import load_dotenv

load_dotenv()


def get_env(key: str) -> str:
    """Get a required environment variable or raise."""
    value = os.getenv(key)
    if not value:
        raise ValueError(f"Missing required environment variable: {key}")
    return value


# Groq
GROQ_API_KEY = get_env("GROQ_API_KEY")

# Supabase
SUPABASE_URL = get_env("SUPABASE_URL")
SUPABASE_ANON_KEY = get_env("SUPABASE_ANON_KEY")

# Tavily
TAVILY_API_KEY = get_env("TAVILY_API_KEY")

# Logfire (optional — graceful if missing)
LOGFIRE_TOKEN = os.getenv("LOGFIRE_TOKEN")
