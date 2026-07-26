# 🎯 Project Ideation Tool

A conversational AI tool that helps builders find a concrete portfolio project idea through a design-thinking interview process.

The tool acts like a UX researcher — interviewing you about your daily work, hobbies, and pain points to surface a real problem worth solving, then handing you a structured project card you can start building from.

**Live demo:** [project-ideation-tool.streamlit.app](https://project-ideation-tool.streamlit.app)

## The Problem

The blocker for most people learning data/AI engineering isn't the curriculum — it's "I have the roadmap, what do I actually build?" Generic project ideas from blog posts and tutorials produce generic portfolios. This tool finds a project grounded in a real problem the user actually cares about.

## How It Works

Three paths depending on where you're starting from:

**Mode 1 — Personal Problem Discovery**
Explores your daily friction, time sinks, and pain points using a bank of 8 invisible "lenses" (manual repetition, information chaos, decision pain, etc.). The bot picks 2-3 lenses based on your background — it doesn't walk through all 8 mechanically. Stops as soon as 2 concrete problems surface.

**Mode 2 — Job/Domain Targeting**
You name a target domain and role. The tool runs live web research (Tavily) to find 3 specific, recurring problems in that space — from engineering blogs, job postings, and industry content. You pick one, and the tool builds a project around it.

**Mode 3 — Both**
Runs personal discovery first, then asks about your target domain. Uses web research to filter solution angles toward that domain — so the project solves your real problem AND signals domain expertise to hiring managers.

Every conversation ends with a structured **project card**:

```
PROBLEM STATEMENT — who, what, context, why
PROJECT — title, description, what makes it yours
INPUT — specific data sources
PROCESSING — specific tools grounded in your tech stack
OUTPUT — specific artifact
SUCCESS METRIC — measurable, testable
INTERVIEW LINE — one sentence for a hiring manager
```

The tool adapts to your tech stack — tell it what you know, paste a curriculum, or share a course link, and it grounds every suggestion in tools you can actually use.

## Conversation Design

The system prompt enforces strict interview discipline:

- **One question per turn** — conversational, not a form
- **No ideas before the problem is confirmed** — prevents anchoring to a technology
- **Pushback on vague answers** — "I do general data stuff" gets redirected to "what specific task did you do last Tuesday?"
- **Smart lens selection** — picks exploration angles based on your background, stops early when signal is strong
- **Domain-aware fallback stacks** — AI engineers get RAG/agents/evals suggested, not a generic web app stack
- **Skill-proof question** — "what should this project prove to an employer?" shapes the tech stack

## Evaluation

The tool is evaluated using an 11-criterion rubric (6 for project card quality, 5 for conversation quality) with 5 disqualifying failure conditions.

### Before/After Prompt Hardening

Real user testing exposed failures: premature project cards, no pushback on vague answers, hallucinated tech stacks. A hardening pass added critical rules, expanded pushback examples, and domain-aware fallback stacks.

| Metric | Before (6 sessions) | After (3 sessions) |
|--------|---------------------|---------------------|
| Average score | 24.8/33 | 30/33 |
| Sessions scoring Strong (28+) | 33% | 100% (completed) |
| Disqualifying failures | 33% | 0% |
| Bot caves to user pressure | 33% | 0% |

The worst "before" session scored 13/33 with 4 disqualifying failures (premature ideas, vague problem, unmeasurable metric, fabricated URL). After the fix, the same test pattern scored 30/33 with zero failures.

### LLM-as-Judge Pipeline

Automated evaluation using `gpt-oss-120b` (different model family from the generator to avoid self-evaluation bias). Each session is scored against all 11 criteria with disqualifying failure checks. The pipeline runs incrementally — saves progress after each session, skips already-scored sessions on re-run.

```bash
uv run python eval/judge.py --input eval/sessions.csv
```

See `eval/manual-scorecard.md` for the full manual evaluation with detailed reasoning per criterion.

## Tech Stack

| Layer | Choice |
|---|---|
| LLM | Groq — `qwen/qwen3.6-27b` |
| Agent Framework | PydanticAI |
| Web Research | Tavily API |
| Auth + DB | Supabase (PostgreSQL + Auth + RLS) |
| Observability | Logfire |
| UI + Deploy | Streamlit / Streamlit Cloud |
| Eval Judge | Groq — `openai/gpt-oss-120b` |

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
uv run python -m streamlit run src/app.py
```

### 6. Run evaluation

```bash
# Export sessions from Supabase SQL Editor as CSV → eval/sessions.csv
uv run python eval/judge.py --input eval/sessions.csv
```

## Project Structure

```
├── src/
│   ├── app.py              # Streamlit UI — auth, sessions, chat loop
│   ├── agent.py            # PydanticAI agent — system prompt, tools
│   ├── database.py         # Supabase CRUD — sessions, messages, briefs
│   ├── tavily_research.py  # Domain research for Mode 2
│   └── config.py           # Environment variable loading
├── eval/
│   ├── judge.py            # LLM-as-judge evaluation pipeline
│   ├── manual-scorecard.md # Manual evaluation of 9 sessions
│   └── sessions.csv        # Exported conversation transcripts
├── supabase/
│   └── schema.sql          # Database schema with RLS policies
├── .devcontainer/
│   ├── devcontainer.json   # Dev Container config
│   └── Dockerfile          # Container image with uv
├── .github/workflows/
│   └── keepalive.yml       # Cron to prevent Supabase free-tier pause
├── pyproject.toml
└── README.md
```

## Key Design Decisions

- **Conversational chatbot, not a questionnaire** — smart lens selection (2-3 from 8), not mechanical walkthrough
- **Supabase for auth + storage** — free tier with keepalive cron, RLS for user isolation
- **Tavily for Mode 2 research** — live web search, not LLM knowledge alone
- **Separate generator and judge models** — Qwen generates, GPT-OSS judges, avoids self-evaluation bias
- **Context truncation** — last 40 messages kept in LLM context to prevent overflow
- **Rate limit retry** — automatic 3-second backoff on Groq rate limits

## Prior Art

The interview framework is inspired by [Alexey Grigorev's](https://github.com/alexeygrigorev) design-thinking prompt for helping students find project ideas: [original gist](https://gist.github.com/alexeygrigorev/c1c8dc3ece5cba91e1e381eeba2706c1). If you prefer voice, ChatGPT voice mode works well with that original prompt.