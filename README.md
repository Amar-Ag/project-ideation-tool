# 🎯 Project Ideation Tool

A conversational AI tool that helps builders find a concrete portfolio project idea through a design-thinking interview process.

The tool acts like a UX researcher — interviewing you about your daily work, hobbies, and pain points to surface a real problem worth solving, then handing you a structured project card you can start building from.

## How It Works

Three paths depending on where you're starting from:

- **Mode 1 — Personal Problem:** Explores your daily friction, time sinks, and pain points to find a problem worth solving
- **Mode 2 — Job/Domain:** Researches recurring problems in your target industry and role
- **Both:** Combines personal discovery with domain targeting

The tool adapts to your tech stack — tell it what you know, paste a curriculum, or share a course link, and it grounds every suggestion in tools you can actually use.

Every conversation ends with a structured **project card**: problem statement, tech stack, success metric, and a one-liner for job interviews.

## Tech Stack

| Layer | Choice |
|---|---|
| LLM | Groq `llama-3.3-70b-versatile` |
| Agent Framework | PydanticAI |
| Web Research | Tavily API |
| Auth + DB | Supabase |
| Observability | Logfire |
| UI + Deploy | Streamlit / Streamlit Cloud |

## Setup

### 1. Clone and install

```bash
git clone https://github.com/Amar-Ag/project-ideation-tool.git
cd project-ideation-tool
pip install uv
uv sync
```

### 2. Set up Supabase

1. Create a project at [supabase.com](https://supabase.com)
2. Go to SQL Editor and run `supabase/schema.sql`
3. Go to Authentication → Settings and enable Email auth

### 3. Get API keys

- **Groq:** [console.groq.com](https://console.groq.com)
- **Tavily:** [tavily.com](https://tavily.com)
- **Logfire** (optional): [logfire.pydantic.dev](https://logfire.pydantic.dev)

### 4. Configure environment

```bash
cp .env.example .env
# Edit .env with your keys
```

### 5. Run locally

```bash
uv run streamlit run src/app.py
```

## Project Structure

```
├── src/
│   ├── app.py              # Streamlit UI + auth + chat loop
│   ├── agent.py            # PydanticAI agent + system prompt
│   ├── database.py         # Supabase CRUD operations
│   ├── tavily_research.py  # Domain research for Mode 2
│   └── config.py           # Environment variable loading
├── supabase/
│   └── schema.sql          # Database schema
├── .devcontainer/
│   ├── devcontainer.json   # Dev Container config
│   └── Dockerfile          # Container image with uv
├── .github/workflows/
│   └── keepalive.yml       # Cron to prevent Supabase free-tier pause
└── pyproject.toml
```

## Prior Art

The interview framework is inspired by [Alexey Grigorev's](https://github.com/alexeygrigorev) design-thinking prompt for helping students find project ideas: [gist](https://gist.github.com/alexeygrigorev/c1c8dc3ece5cba91e1e381eeba2706c1).
