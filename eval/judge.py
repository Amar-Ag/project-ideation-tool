"""
LLM-as-Judge Evaluation Pipeline for the Project Ideation Tool.

Reads conversation transcripts from a CSV export (Supabase messages table),
scores each session against the 11-criterion rubric using a judge LLM,
and outputs results as JSON + markdown.

Usage:
    uv run python eval/judge.py --input eval/sessions.csv --output eval/results.json

The CSV must have columns: session_id, mode, role, content, created_at
(same format as the Supabase SQL Editor export)
"""

import argparse
import csv
import json
import time
from pathlib import Path

from groq import Groq

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

JUDGE_MODEL = "openai/gpt-oss-120b"
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds


# ---------------------------------------------------------------------------
# Rubric — each criterion as a judge prompt
# ---------------------------------------------------------------------------

CRITERIA = [
    {
        "id": 1,
        "name": "Problem Specificity",
        "part": "card",
        "prompt": """Score the PROBLEM STATEMENT on specificity.

3 = Names a specific WHO, specific WHAT (the pain), specific CONTEXT, and specific WHY.
    Example of a 3: "Data analysts at retail companies spend 2-3 hours every Monday on manual report generation because their data lives in 3 separate systems"
2 = Right domain but missing context or scale.
    Example of a 2: "Data analysts spend time on manual reporting"
1 = No specific who, what, or context.
    Example of a 1: "People have trouble managing their data"

The test: Could you draw a picture of the person who has this problem and what their Monday looks like? If yes, score 3.""",
    },
    {
        "id": 2,
        "name": "Project Concreteness",
        "part": "card",
        "prompt": """Score the PROJECT description on concreteness.

3 = You can tell exactly what the system does. A developer could start building from this description without clarifying questions.
2 = Right idea but too abstract to build from.
1 = Could mean anything. "An AI-powered productivity app."

The test: Could a developer start building from this description without asking a single clarifying question?""",
    },
    {
        "id": 3,
        "name": "Input/Processing/Output Completeness",
        "part": "card",
        "prompt": """Score the INPUT, PROCESSING, and OUTPUT sections.

For each component:
- Pass: Specific data sources/tools/artifacts named
- Partial: Category named but not specific
- Fail: Missing or vague ("data", "AI does it", "insights")

3 = All three (Input, Processing, Output) pass
2 = Two pass, one is partial or fails
1 = Multiple fails or fundamentally incomplete""",
    },
    {
        "id": 4,
        "name": "Tech Stack Appropriateness",
        "part": "card",
        "prompt": """Score the tech stack suggestion.

3 = Stack uses tools the user stated they know or are learning, and scope is realistic for 4-6 weeks solo.
2 = Stack is appropriate but includes something the user didn't mention knowing, without explanation.
1 = Stack is over-engineered, relies on tools the user hasn't mentioned, or gives no guidance.

Important: If the user explicitly said they have no tech preferences, a reasonable default stack scores 2 (not 1), as long as it fits the problem.""",
    },
    {
        "id": 5,
        "name": "Success Metric Quality",
        "part": "card",
        "prompt": """Score the SUCCESS METRIC.

3 = Measurable, specific, directly connected to the stated problem.
    Example: "Monday reports generated in under 5 minutes with zero manual steps"
2 = Directionally correct but not measurable.
    Example: "Reports are generated automatically"
1 = Vague, unmeasurable, or missing.
    Example: "Users will be happy" / "improves productivity"

The test: Could you run an experiment and definitively say "pass" or "fail" on this metric?""",
    },
    {
        "id": 6,
        "name": "Interview Readiness",
        "part": "card",
        "prompt": """Score the interview readiness of the project card.

3 = Includes a specific, personal one-liner the user can say out loud AND addresses "why my version matters" if similar things exist.
    Example: "I was spending 300 hours a year copying data between spreadsheets"
2 = Has a reasonable angle but it's generic ("I wanted to learn data engineering") rather than personal.
1 = No interview angle, or purely technology-driven ("I wanted to try LLMs") with no connection to a real problem.""",
    },
    {
        "id": 7,
        "name": "Question Discipline",
        "part": "conversation",
        "prompt": """Score the bot's question discipline across the FULL conversation.

3 = Every bot turn asks one question, occasionally two when closely related. Never more.
2 = Mostly one question per turn, but one or two turns have 3+ questions.
1 = Multiple turns with bullet-pointed question lists — behaving like a form, not a conversation.

Count the questions in each bot turn. If any turn has 3 or more distinct questions, it cannot score 3.""",
    },
    {
        "id": 8,
        "name": "Pushback Quality",
        "part": "conversation",
        "prompt": """Score how well the bot pushes back on vague user answers.

3 = When the user gave a vague answer (e.g. "just general data stuff", "both", "yes", "it's fine"), the bot explicitly asked for a specific example before moving on. Never accepted "I don't know" without pushing or offering a concrete exercise.
2 = Pushed back in most cases but let one or two vague answers through.
1 = Accepted vague answers and moved forward.

Find the most vague user answer in the conversation. Did the bot push back? If not, it cannot score 3.""",
    },
    {
        "id": 9,
        "name": "Lens Selection Logic",
        "part": "conversation",
        "prompt": """Score the bot's lens selection approach. The bot has 8 internal "lenses" (friction, time sinks, manual repetition, etc.) it uses to explore problems. These should be INVISIBLE to the user.

3 = Bot picked lenses matching the user's background, stopped when it had enough signal. Never mentioned lenses by name.
2 = Lenses were reasonable but felt mechanical, or the bot always starts with the same lens regardless of user.
1 = Bot walked through all 8 lenses in order, or mentioned the lens framework by name to the user.

Note: For Mode 2 (domain) sessions, lens selection is not applicable — score N/A.
Note: If the user arrived with a specific project idea, the bot may skip traditional lens exploration and instead dig into that idea's underlying problem — this is acceptable and can score 3 if done well.""",
    },
    {
        "id": 10,
        "name": "Idea Timing",
        "part": "conversation",
        "prompt": """Score when the bot first suggested project ideas, solution angles, or tech stack recommendations.

3 = No project ideas, solution angles, or tech stacks surfaced until AFTER the problem statement was confirmed by the user.
2 = One minor hint toward a solution slipped through early, but didn't derail problem discovery.
1 = Bot suggested a project idea, solution angle, or tech stack during the background/exploration phase, before a problem statement was established.

This is a DISQUALIFYING failure if score is 1. The bot must never suggest ideas before the problem is confirmed.""",
    },
    {
        "id": 11,
        "name": "Synthesis Timing",
        "part": "conversation",
        "prompt": """Score whether the bot moved to problem statement synthesis at the right moment.

3 = Bot synthesized when it had 1-2 specific, concrete problems with enough detail. Not too early, not too late.
2 = Slightly early (problem wasn't fully specific) or slightly late (one extra round that didn't add value).
1 = Bot either synthesized from a vague problem (output will be generic) or kept asking long past the point of diminishing return.""",
    },
]

DISQUALIFYING_CHECKS = """Check for these disqualifying failures. Return true/false for each:

D1: Does the problem statement have NO specific WHO? (just "people" or "users")
D2: Is the success metric unmeasurable? ("users will find it useful", "improves productivity")
D3: Did the bot suggest a project idea, solution angle, or tech stack BEFORE the problem statement was established and confirmed?
D4: Does the tech stack require custom model training from scratch?
D5: Is the Input OR Output section missing or too vague to build from?

Return JSON: {"D1": true/false, "D2": true/false, "D3": true/false, "D4": true/false, "D5": true/false}
Only return the JSON, nothing else."""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def load_sessions(csv_path: str) -> dict:
    """Load sessions from CSV export, grouped by session_id."""
    sessions = {}
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sid = row["session_id"]
            if sid not in sessions:
                sessions[sid] = {"mode": row["mode"], "messages": []}
            sessions[sid]["messages"].append(
                {
                    "role": row["role"],
                    "content": row["content"],
                }
            )
    return sessions


def format_transcript(messages: list[dict]) -> str:
    """Format messages into a readable transcript."""
    lines = []
    for m in messages:
        role = "User" if m["role"] == "user" else "Agent"
        lines.append(f"{role}: {m['content']}")
        lines.append("")
    return "\n".join(lines)


def call_judge(client: Groq, system_prompt: str, user_prompt: str) -> str:
    """Call the judge model with retry logic for rate limits."""
    for attempt in range(MAX_RETRIES):
        try:
            response = client.chat.completions.create(
                model=JUDGE_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.0,
                max_tokens=500,
            )
            return (response.choices[0].message.content or "").strip()
        except Exception as e:
            error_msg = str(e).lower()
            if (
                "rate" in error_msg or "limit" in error_msg
            ) and attempt < MAX_RETRIES - 1:
                print(
                    f"  Rate limit hit, waiting {RETRY_DELAY}s (attempt {attempt + 1}/{MAX_RETRIES})"
                )
                time.sleep(RETRY_DELAY)
                continue
            raise
    return ""


def parse_score(response: str) -> int:
    """Extract a numeric score (1-3) from the judge response."""
    # Look for the score in common formats
    for line in response.split("\n"):
        line = line.strip()
        # "Score: 3" or "**Score: 3**" or "3/3"
        if "score" in line.lower():
            for char in line:
                if char in "123":
                    return int(char)
        # Just a number on its own line
        if line in ("1", "2", "3"):
            return int(line)
    # Fallback: find first 1, 2, or 3 in the response
    for char in response:
        if char in "123":
            return int(char)
    return 0  # Could not parse


def parse_disqualifying(response: str) -> dict:
    """Parse D1-D5 check results from judge response."""
    # Strip markdown code fences if present
    cleaned = response.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Fallback: try to find JSON in the response
        start = cleaned.find("{")
        end = cleaned.rfind("}") + 1
        if start >= 0 and end > start:
            try:
                return json.loads(cleaned[start:end])
            except json.JSONDecodeError:
                pass
    return {"D1": False, "D2": False, "D3": False, "D4": False, "D5": False}


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------


def evaluate_session(client: Groq, session_id: str, session_data: dict) -> dict:
    """Evaluate a single session against all criteria."""
    transcript = format_transcript(session_data["messages"])
    mode = session_data["mode"] or "unknown"

    print(f"\nEvaluating session {session_id[:8]} (mode={mode})...")

    # Check if session produced a project card (needed for Part 1)
    has_card = any(
        "PROBLEM STATEMENT" in m["content"].upper()
        for m in session_data["messages"]
        if m["role"] == "assistant"
    )

    result = {
        "session_id": session_id,
        "mode": mode,
        "message_count": len(session_data["messages"]),
        "has_card": has_card,
        "criteria": {},
        "disqualifying": {},
        "total": 0,
        "verdict": "",
    }

    # Step 1: Disqualifying failure check (only if card exists)
    if has_card:
        print("  Checking disqualifying failures...")
        dq_response = call_judge(
            client,
            "You are evaluating a project ideation conversation. Check for disqualifying failures.",
            f"Conversation transcript:\n\n{transcript}\n\n{DISQUALIFYING_CHECKS}",
        )
        result["disqualifying"] = parse_disqualifying(dq_response)
        time.sleep(1)  # Rate limit spacing

    # Step 2: Score each criterion
    system = (
        "You are an expert evaluator scoring a project ideation conversation. "
        "You will be given a scoring criterion and a conversation transcript. "
        "Score the conversation on this criterion using the provided rubric. "
        "Respond with:\n"
        "Score: [1, 2, or 3]\n"
        "Reason: [One sentence explaining your score]"
    )

    total = 0
    for criterion in CRITERIA:
        cid = criterion["id"]
        name = criterion["name"]

        # Skip card criteria if no card was generated
        if criterion["part"] == "card" and not has_card:
            print(f"  Criterion {cid} ({name}): SKIPPED (no card)")
            result["criteria"][cid] = {
                "name": name,
                "score": None,
                "reason": "No project card generated — session incomplete",
            }
            continue

        # Skip lens selection for Mode 2
        if cid == 9 and mode == "domain":
            print(f"  Criterion {cid} ({name}): N/A (Mode 2)")
            result["criteria"][cid] = {
                "name": name,
                "score": 3,  # N/A counted as pass
                "reason": "Mode 2 — lens selection not applicable",
            }
            total += 3
            continue

        user_prompt = (
            f"## Criterion: {name}\n\n"
            f"{criterion['prompt']}\n\n"
            f"## Conversation Transcript\n\n{transcript}"
        )

        print(f"  Criterion {cid} ({name})...", end=" ", flush=True)
        response = call_judge(client, system, user_prompt)
        score = parse_score(response)

        # Extract reason
        reason = ""
        for line in response.split("\n"):
            if line.strip().lower().startswith("reason:"):
                reason = line.strip()[7:].strip()
                break
        if not reason:
            reason = response[:200]

        result["criteria"][cid] = {
            "name": name,
            "score": score,
            "reason": reason,
        }
        total += score
        print(f"{score}/3")

        time.sleep(1)  # Rate limit spacing

    result["total"] = total
    max_score = 33

    # Determine verdict
    any_dq = any(result["disqualifying"].get(f"D{i}", False) for i in range(1, 6))
    if any_dq:
        result["verdict"] = "Disqualifying failure"
    elif total >= 28:
        result["verdict"] = "Strong"
    elif total >= 22:
        result["verdict"] = "Acceptable"
    else:
        result["verdict"] = "Needs rework"

    print(f"  TOTAL: {total}/{max_score} — {result['verdict']}")
    if any_dq:
        dq_flags = [k for k, v in result["disqualifying"].items() if v]
        print(f"  DISQUALIFYING: {', '.join(dq_flags)}")

    return result


def results_to_markdown(results: list[dict]) -> str:
    """Convert results to a readable markdown summary."""
    lines = [
        "# LLM-as-Judge Evaluation Results",
        f"\n**Judge model:** {JUDGE_MODEL}",
        f"**Sessions evaluated:** {len(results)}",
        "",
        "## Summary",
        "",
        "| # | Session | Mode | Score | Verdict | D-Failures |",
        "|---|---------|------|-------|---------|------------|",
    ]

    for i, r in enumerate(results, 1):
        sid = r["session_id"][:8]
        dq_flags = [k for k, v in r["disqualifying"].items() if v]
        dq_str = ", ".join(dq_flags) if dq_flags else "None"
        lines.append(
            f"| {i} | {sid} | {r['mode']} | {r['total']}/33 | {r['verdict']} | {dq_str} |"
        )

    lines.append("")

    # Detail per session
    for r in results:
        sid = r["session_id"][:8]
        lines.append(f"\n## Session {sid} (mode={r['mode']})")
        lines.append(f"**Score: {r['total']}/33 — {r['verdict']}**\n")
        lines.append("| # | Criterion | Score | Reason |")
        lines.append("|---|-----------|-------|--------|")

        for cid in range(1, 12):
            c = r["criteria"].get(cid, {})
            name = c.get("name", "?")
            score = c.get("score", "N/A")
            reason = c.get("reason", "")[:100]
            score_str = f"{score}/3" if score is not None else "SKIP"
            lines.append(f"| {cid} | {name} | {score_str} | {reason} |")

        dq_flags = [k for k, v in r["disqualifying"].items() if v]
        if dq_flags:
            lines.append(f"\n**Disqualifying failures:** {', '.join(dq_flags)}")
        lines.append("")

    return "\n".join(lines)


def load_existing_results(output_path: str) -> list[dict]:
    """Load previously scored results from JSON, if file exists."""
    path = Path(output_path)
    if path.exists():
        with open(path, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate ideation sessions with LLM-as-judge"
    )
    parser.add_argument(
        "--input", required=True, help="Path to CSV export from Supabase"
    )
    parser.add_argument(
        "--output", default="eval/results.json", help="Path for JSON results"
    )
    parser.add_argument(
        "--markdown", default="eval/results.md", help="Path for markdown report"
    )
    parser.add_argument(
        "--session", default=None, help="Evaluate a single session ID (prefix match)"
    )
    parser.add_argument(
        "--rerun",
        action="store_true",
        help="Re-evaluate sessions even if already scored",
    )
    args = parser.parse_args()

    # Load sessions from CSV
    sessions = load_sessions(args.input)
    print(f"Loaded {len(sessions)} sessions from {args.input}")

    # Filter to single session if requested
    if args.session:
        sessions = {
            sid: data for sid, data in sessions.items() if sid.startswith(args.session)
        }
        if not sessions:
            print(f"No session found matching '{args.session}'")
            return

    # Load existing results and figure out what's already scored
    existing_results = load_existing_results(args.output)
    scored_ids = {r["session_id"] for r in existing_results}

    if not args.rerun:
        pending = {sid: data for sid, data in sessions.items() if sid not in scored_ids}
        skipped = len(sessions) - len(pending)
        if skipped > 0:
            print(f"Skipping {skipped} already-scored sessions (use --rerun to force)")
        sessions = pending

    if not sessions:
        print("All sessions already scored. Nothing to do.")
        # Still regenerate markdown from existing results
        md_path = Path(args.markdown)
        md_report = results_to_markdown(existing_results)
        with open(md_path, "w") as f:
            f.write(md_report)
        print(f"Markdown report regenerated at {md_path}")
        return

    # Initialize Groq client
    import os

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        from dotenv import load_dotenv

        load_dotenv()
        api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("ERROR: GROQ_API_KEY not set")
        return

    client = Groq(api_key=api_key)

    # Evaluate pending sessions
    new_results = []
    for sid, data in sessions.items():
        try:
            result = evaluate_session(client, sid, data)
            new_results.append(result)

            # Save after each session so progress isn't lost on crash/rate limit
            if args.rerun:
                # Replace existing entry if re-running
                all_results = [r for r in existing_results if r["session_id"] != sid]
                all_results.extend(new_results)
            else:
                all_results = existing_results + new_results

            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as f:
                json.dump(all_results, f, indent=2)

        except Exception as e:
            print(f"  ERROR evaluating {sid[:8]}: {e}")
            print(f"  Progress saved — {len(new_results)} new sessions scored this run")
            break

    # Merge all results and save final outputs
    if args.rerun:
        # Replace any re-run sessions in existing results
        rerun_ids = {r["session_id"] for r in new_results}
        all_results = [r for r in existing_results if r["session_id"] not in rerun_ids]
        all_results.extend(new_results)
    else:
        all_results = existing_results + new_results

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\nJSON results saved to {output_path} ({len(all_results)} total sessions)")

    # Generate markdown report from ALL results
    md_path = Path(args.markdown)
    md_report = results_to_markdown(all_results)
    with open(md_path, "w") as f:
        f.write(md_report)
    print(f"Markdown report saved to {md_path}")

    # Print summary
    print("\n" + "=" * 60)
    print(
        f"This run: {len(new_results)} new | {len(existing_results)} existing | {len(all_results)} total"
    )
    print("=" * 60)


if __name__ == "__main__":
    main()
