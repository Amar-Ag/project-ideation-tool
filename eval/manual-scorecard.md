# Evaluation Scorecard — All 9 Sessions
## Project Ideation Tool — Manual Evaluation

**Evaluator:** Amar + Claude  
**Date:** 2026-07-13  
**Rubric version:** output-quality-rubric.md (11 criteria, 33 points)

---

## Scoring Key

- **3 = Pass** — clearly meets the bar
- **2 = Partial** — close but missing something specific
- **1 = Fail** — does not meet the bar
- **Strong:** 28-33 | **Acceptable:** 22-27 | **Needs rework:** <22
- **D1-D5:** Disqualifying failures (auto-fail regardless of score)

---

## BEFORE Prompt Hardening (Sessions 1-6)

### Session 1: "The Self-Serve Excel Generator"
- **ID:** 13734282 | **Mode:** Personal | **Date:** 2026-07-02
- **Persona:** Data scientist, SQL/Python/Power BI, ad-hoc report requests
- **Project:** Text-to-SQL → auto-generated Excel with pivots

| # | Criterion | Score | Notes |
|---|-----------|-------|-------|
| 1 | Problem Specificity | 3 | "A Data Scientist experiences massive rework when responding to ad-hoc stakeholder requests because the initial data delivery is a static Excel file" |
| 2 | Project Concreteness | 3 | Text-to-SQL + openpyxl pivot generation — buildable spec |
| 3 | Input/Processing/Output | 3 | Input: SQL warehouse + natural language. Processing: LLM text-to-SQL + pandas + openpyxl. Output: Excel with pivots and slicers |
| 4 | Tech Stack | 3 | Python, SQL, LLM API, openpyxl — all user-stated or natural extensions |
| 5 | Success Metric | 2 | Implied (eliminates rework) but not stated as a measurable number |
| 6 | Interview Readiness | 3 | Personal pain, specific story |
| 7 | Question Discipline | 2 | Turn 4 bundles "typical Tuesday" + "tech stack" |
| 8 | Pushback Quality | 3 | "That 'varies' is the juicy part" — excellent |
| 9 | Lens Selection | 3 | Time sinks + manual repetition, stopped early with strong signal |
| 10 | Idea Timing | 3 | Problem confirmed before solutions |
| 11 | Synthesis Timing | 3 | Right moment |
| | **TOTAL** | **31/33** | **Strong** |

**Disqualifying failures:** None  
**Verdict:** Best session in the pre-fix batch. Gold standard for Mode 1.

---

### Session 2: "The Eligibility Engine"
- **ID:** b753bc66 | **Mode:** Domain | **Date:** 2026-07-02
- **Persona:** Aspiring AI engineer targeting healthcare insurance/pharma
- **Project:** Clinical trial patient matching via dynamic SQL generation

| # | Criterion | Score | Notes |
|---|-----------|-------|-------|
| 1 | Problem Specificity | 3 | "Pharma and research teams experience significant delays in trial recruitment because finding matching patients is manual and error-prone across fragmented data" |
| 2 | Project Concreteness | 3 | Ingests criteria JSON, generates SQL queries, filters patient DB |
| 3 | Input/Processing/Output | 3 | Input: trial criteria JSON + patient DB. Processing: Python dynamic SQL. Output: ranked eligible patient IDs |
| 4 | Tech Stack | 3 | Python + SQL — exactly user's stated skills |
| 5 | Success Metric | 2 | Not fully visible (truncated in export) |
| 6 | Interview Readiness | 2 | No personal connection — user explicitly said so. Bot pivoted to "technical frustration" narrative |
| 7 | Question Discipline | 2 | First turn asks domain + role + company (3-in-1, standard for Mode 2 but borderline) |
| 8 | Pushback Quality | 2 | Accepted "lets go with the 2" and "1" without asking why |
| 9 | Lens Selection | N/A | Mode 2 — scored as 3/3 (no lens exploration needed) |
| 10 | Idea Timing | 3 | Problems presented after Tavily research |
| 11 | Synthesis Timing | 3 | Clean flow |
| | **TOTAL** | **27/33** | **Acceptable** |

**Disqualifying failures:** None  
**Notes:** Weakest point is interview readiness — no personal story. Bot correctly asked "do you have personal experience?" (Mode 2 behavior) but answer was no.

---

### Session 3: "CompGuard v1"
- **ID:** 9dfd960e | **Mode:** Both | **Date:** 2026-07-02
- **Persona:** Data scientist → AI engineering, commission calculation pain
- **Project:** Email extraction → policy validation → commission automation

| # | Criterion | Score | Notes |
|---|-----------|-------|-------|
| 1 | Problem Specificity | 3 | Data professionals, commission calculation, monthly payroll, unstructured emails |
| 2 | Project Concreteness | 2 | "Combo of all 3" angles — overscoped, unclear MVP |
| 3 | Input/Processing/Output | 2 | Described but combining 3 approaches makes scope fuzzy |
| 4 | Tech Stack | 2 | LangChain + PostgreSQL suggested when user said "I am new to this so you suggest" — not grounded in user's skills |
| 5 | Success Metric | 2 | Implied but no clear measurable number |
| 6 | Interview Readiness | 3 | "Gut-level hatred for the Excel friction" — strong personal connection |
| 7 | Question Discipline | 2 | First response bundles background + tools |
| 8 | Pushback Quality | 2 | Accepted "yes" without verification |
| 9 | Lens Selection | 3 | Focused on right signals |
| 10 | Idea Timing | 3 | Problem statement before solutions |
| 11 | Synthesis Timing | 2 | "Both" path incomplete — no explicit domain question, no Tavily |
| | **TOTAL** | **26/33** | **Acceptable** |

**Disqualifying failures:** None (borderline D3 — tech stack came in same message as card)  
**Notes:** "Both" path didn't fully execute. Missing mandatory domain question and Tavily research.

---

### Session 4: "Claim Denial Detective"
- **ID:** f8018245 | **Mode:** Both | **Date:** 2026-07-06
- **Persona:** Data scientist in logistics → healthcare AI engineering
- **Project:** Claims cross-referenced against insurance PDFs for denial auditing

| # | Criterion | Score | Notes |
|---|-----------|-------|-------|
| 1 | Problem Specificity | 3 | Hospital clinics, coding staff, claim denials, PDF guidelines disconnected from claims data |
| 2 | Project Concreteness | 3 | Cross-references claims against PDFs, flags incorrect denials, shows source text |
| 3 | Input/Processing/Output | 3 | Input: insurance PDFs + synthetic claims CSV. Processing: PDF parsing + embeddings + ChromaDB + LLM. Output: Streamlit dashboard with audit notes |
| 4 | Tech Stack | 3 | Python, SQL, ChromaDB, pdfplumber, LLM API, Streamlit — appropriate |
| 5 | Success Metric | 3 | "90% accuracy identifying triggering text from PDFs" — measurable, specific |
| 6 | Interview Readiness | 3 | "I was spending hundreds of hours manually translating complex logistics contracts" — bridges personal experience to healthcare domain |
| 7 | Question Discipline | 2 | First response bundles background + tools |
| 8 | Pushback Quality | 2 | Accepted "i think they both did a little" and "maybe healthcare" |
| 9 | Lens Selection | 3 | Good selection based on user's signals |
| 10 | Idea Timing | 3 | Correct sequence |
| 11 | Synthesis Timing | 3 | Asked domain question at the right moment — "both" path executed correctly |
| | **TOTAL** | **31/33** | **Strong** |

**Disqualifying failures:** None  
**Notes:** Best "both" mode execution. Domain question asked correctly, solution angles filtered to healthcare. Gold standard for combined path.

---

### Session 5: "EdTech Exam Platform" (BEFORE fix)
- **ID:** d1d2de5f | **Mode:** Personal | **Date:** 2026-07-10
- **Persona:** EdTech founder, no tech preferences
- **Project:** Data labeling platform for exam quality (incomplete)

| # | Criterion | Score | Notes |
|---|-----------|-------|-------|
| 1 | Problem Specificity | 3 | "EdTech founders experience bottlenecks in exam quality when scaling because LLMs default to generic knowledge" |
| 2 | Project Concreteness | 2 | Two solution angles presented but user never picked one |
| 3 | Input/Processing/Output | 2 | Partially defined — no final card generated |
| 4 | Tech Stack | 1 | FastAPI + PostgreSQL + Next.js suggested, then switched to Streamlit + LlamaIndex + SQLite. User said "no preferences" — bot generated from training data, no skill-proof question |
| 5 | Success Metric | 1 | Never generated — conversation ended prematurely |
| 6 | Interview Readiness | 2 | Founder narrative strong but never formalized |
| 7 | Question Discipline | 2 | Turn 7 asks connection check + tools (2 questions) |
| 8 | Pushback Quality | 3 | Good — pushed "I already know what I want" back to discovery |
| 9 | Lens Selection | 2 | User came with idea, bot didn't use lenses but did dig |
| 10 | Idea Timing | 1 | **DISQUALIFYING.** Tech stack IN same message as problem statement, before solution angles |
| 11 | Synthesis Timing | 2 | Problem + tech bundled prematurely |
| | **TOTAL** | **21/33** | **Needs rework** |

**Disqualifying failures:** D3 — Tech stack suggested before Step 4  
**Notes:** Bot correctly pushed back on "I already know what I want" but then bundled problem statement with tech stack, skipping solution angles entirely.

---

### Session 6: "Conflict Resolution Coach" (BEFORE fix)
- **ID:** af5ef08e | **Mode:** Personal | **Date:** 2026-07-13
- **Persona:** External tester, wants to build voice conflict resolution coach
- **Project:** Voice-based conflict resolution coach (multiple versions generated)

| # | Criterion | Score | Notes |
|---|-----------|-------|-------|
| 1 | Problem Specificity | 1 | "A professional experiences frustration when work is not recognized" — could be anyone |
| 2 | Project Concreteness | 2 | Voice coach described as feature list, not buildable spec |
| 3 | Input/Processing/Output | 1 | Input: "voice interactions." Processing: "NLP and ML." Output: "personalized coaching." All vague |
| 4 | Tech Stack | 1 | React/Angular/Vue/Flask/Django/CLIPS/PyKE — all from LLM training data, user never stated knowing any |
| 5 | Success Metric | 1 | "Reduction in conflict escalation and improvement in user satisfaction" — unmeasurable |
| 6 | Interview Readiness | 1 | Generic, no personal story |
| 7 | Question Discipline | 2 | Several turns bundle 2-3 questions |
| 8 | Pushback Quality | 1 | Accepted "both", "YESSS", "that is based on voice" — no pushback |
| 9 | Lens Selection | 1 | Mentioned "friction lens" by name (should be invisible), then abandoned |
| 10 | Idea Timing | 1 | **DISQUALIFYING.** Full project card at turn 7 during Step 1/2 |
| 11 | Synthesis Timing | 1 | Synthesized from almost no concrete detail |
| | **TOTAL** | **13/33** | **Needs significant rework** |

**Disqualifying failures:** D1, D2, D3, D5  
**Notes:** Worst session. Bot lost control of interview, user drove conversation, tech stack hallucinated, fabricated Coursera URL. This session triggered the prompt hardening.

---

## AFTER Prompt Hardening (Sessions 7-9)

### Session 7: "ExamGap AI" (AFTER fix — same pattern as Session 5)
- **ID:** 88073d3f | **Mode:** Personal | **Date:** 2026-07-14
- **Persona:** TA building edtech exam platform, no tech preferences
- **Project:** Syllabus gap analyzer with RAG-based question generation

| # | Criterion | Score | Notes |
|---|-----------|-------|-------|
| 1 | Problem Specificity | 3 | "TAs and instructors struggle to create high-quality, non-repetitive exam questions that cover the full curriculum because they manually sift through hundreds of slides, relying on best judgment instead of data" |
| 2 | Project Concreteness | 3 | "ExamGap AI" — upload syllabus + slides, identifies gaps, generates questions |
| 3 | Input/Processing/Output | 3 | Input: syllabus PDF + lecture slides. Processing: PyPDF2 + SentenceTransformers + ChromaDB + LangChain + LLM. Output: dashboard showing covered/missing objectives with generated questions |
| 4 | Tech Stack | 2 | AI-native stack selected after skill-proof question — correct process, but still generated since user had no preferences |
| 5 | Success Metric | 2 | "Identify 3 gaps and generate passable questions" — testable but qualitative |
| 6 | Interview Readiness | 3 | "As a TA, I realized exam creation was a guessing game — so I built an AI pipeline" — personal, specific |
| 7 | Question Discipline | 2 | Turn 3 and Turn 11 bundle multiple questions |
| 8 | Pushback Quality | 3 | Held firm on "I already know what I want" AND "I don't have tech preferences" (twice) |
| 9 | Lens Selection | 3 | Quality/errors + time sinks based on TA experience |
| 10 | Idea Timing | 3 | Problem at Turn 15, angles at Turn 17, card at Turn 19 — perfect sequence |
| 11 | Synthesis Timing | 3 | Right moment — had specifics about slides, syllabus, past questions |
| | **TOTAL** | **30/33** | **Strong** |

**Disqualifying failures:** None  
**Comparison to Session 5 (same pattern):** 21/33 → 30/33 (+9 points, D3 eliminated)

Key improvements:
- Bot said "We'll pick the tech stack once the problem is concrete" (Rule 2 working)
- Asked "what should this project prove to a hiring manager?" (skill-proof question working)
- Solution angles presented BEFORE tech stack (correct Step 4→5→6 sequence)

---

### Session 8: "The Driver" (AFTER fix — same pattern as Session 6)
- **ID:** 51cb1ade | **Mode:** Personal | **Date:** 2026-07-14
- **Persona:** Stress test — user skips background, demands tech stack
- **Project:** N/A — conversation intentionally cut short after 7 messages

| # | Criterion | Score | Notes |
|---|-----------|-------|-------|
| 7 | Question Discipline | 3 | One clean question per turn |
| 8 | Pushback Quality | 3 | "I want to make sure we pin down a real pain point, not just a cool toy" + "That's exactly the wrong place to start" |
| 10 | Idea Timing | 3 | Bot refused to give ideas or tech stack when pushed |

**Incomplete — cannot score Part 1 (no card generated)**  
**Conversation quality: 3/3 on all testable criteria**  
**Notes:** Two firm redirects in a row. Before the fix, this pattern produced a full tech stack dump at turn 5 (Session 6). Now the bot holds its ground.

---

### Session 9: "The One-Worder" (AFTER fix — pushback stress test)
- **ID:** 25b3939c | **Mode:** Personal | **Date:** 2026-07-14
- **Persona:** Stress test — gives minimal one-word answers
- **Project:** N/A — conversation intentionally cut short after 7 messages

| # | Criterion | Score | Notes |
|---|-----------|-------|-------|
| 7 | Question Discipline | 3 | Clean single questions |
| 8 | Pushback Quality | 3 | "data stuff" → "I need something more specific — what specific task did you do last Tuesday?" / "its fine" → "'it's fine' doesn't give me the signal I need" |

**Incomplete — cannot score Part 1 (no card generated)**  
**Conversation quality: 3/3 on all testable criteria**  
**Notes:** Both pushback examples from Rule 3 fired correctly. Bot held ground twice on consecutive one-word answers.

---

## Summary

### Score Distribution

| # | Session | Mode | Score | Verdict | D-Failures | Phase |
|---|---------|------|-------|---------|------------|-------|
| 1 | Self-Serve Excel | Personal | 31/33 | Strong | None | Before |
| 2 | Eligibility Engine | Domain | 27/33 | Acceptable | None | Before |
| 3 | CompGuard v1 | Both | 26/33 | Acceptable | None (borderline) | Before |
| 4 | Claim Denial Detective | Both | 31/33 | Strong | None | Before |
| 5 | EdTech Exam (before) | Personal | 21/33 | Needs rework | D3 | Before |
| 6 | Conflict Resolution | Personal | 13/33 | Needs rework | D1,D2,D3,D5 | Before |
| 7 | ExamGap AI (after) | Personal | 30/33 | Strong | None | After |
| 8 | The Driver (after) | Personal | N/A | Behavior pass | None | After |
| 9 | The One-Worder (after) | Personal | N/A | Behavior pass | None | After |

### Before vs After

| Metric | Before (6 sessions) | After (3 sessions) |
|--------|---------------------|---------------------|
| Average score (completed) | 24.8/33 | 30/33 |
| Sessions scoring Strong (28+) | 2 of 6 (33%) | 1 of 1 (100%) |
| Disqualifying failures | 2 of 6 (33%) | 0 of 3 (0%) |
| Bot caves to user pressure | 2 of 6 | 0 of 3 |
| Tech stack from training data (no user input) | 2 of 6 | 0 of 3 |

### What works well
- Problem discovery flow when bot follows process (Sessions 1, 4, 7)
- Pushback on vague answers (Sessions 1, 7, 8, 9)
- "Both" mode with mandatory domain question (Session 4)
- Tech stack grounded in user's stated skills (Sessions 1, 2)
- Skill-proof question ("what should this project prove?") shaping stack (Session 7)

### What still needs work
- Question discipline — first response often bundles 2 questions (all sessions)
- Pushback on short confirmations ("yes", "1", "lets go with 2") — bot accepts these
- Success metrics occasionally qualitative rather than measurable
- Tech stack for users with "no preferences" is still generated from LLM knowledge (acceptable but not ideal)

### Prompt changes that drove improvement
1. **Critical rules section** at top of system prompt — "NEVER suggest tech before Step 4"
2. **Rule 9** — "If user tries to skip, redirect firmly" with exact phrasing
3. **Expanded Rule 3** — four specific vague-answer examples with pushback responses
4. **Rule 8** — "If user arrives with idea, park it and dig into the problem"
5. **"NEVER generate tech from training data"** in critical rules
6. **Skill-proof question** — "what should this project prove to an employer?"
7. **Domain-aware fallback stacks** — AI engineering gets RAG/agents/evals, not web app stack
