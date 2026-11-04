# Quiz Mentor — AI-Engine (AI Development Branch)

This README is for anyone working on the AI side of Quiz Mentor. It's
not the full architecture doc — just enough to understand what this
branch is building, why it's built the way it is, and how to run what
exists so far.

## What the AI-engine is responsible for

Given a user and their current skill profile, decide **what language**
and **what difficulty** to ask next, generate an actual question for
that language/difficulty, and update what the system knows about the
user after they answer. That's the whole job — the backend owns
auth/sessions/storage orchestration, the AI-engine owns the quiz logic.

## Key decision: no Ollama, no model training

Early planning considered training/fine-tuning a model and running it
via Ollama. That's not what this branch does, deliberately:

- **No fine-tuning.** Training needs labeled data, GPU time, and
  maintenance that doesn't fit a project this size or timeline.
- **Instead: RAG (Retrieval-Augmented Generation).** Reference material
  (PDFs, notes, past papers, datasets) gets chunked and embedded into a
  vector store. When a question is needed, the engine retrieves the
  relevant chunks and feeds them into a prompt sent to an LLM API
  (Claude or OpenAI). The LLM generates the question; nothing about the
  model itself changes.
- This is *why* uploading a new book or PDF can "update" the system
  immediately — it just becomes retrievable material for the next
  prompt, with zero retraining involved.

## The adaptive rule (core logic)

- **Trials 1–30 ("profiling phase")**: pick a random language each
  time, always beginner difficulty. Goal is to get a first read on every
  language the user touches.
- **Trial 31+ ("adaptive phase")**: weight language selection toward
  whichever languages show the *lowest accuracy* so far. Difficulty
  tracks the user's current per-language level (nudges up on correct
  answers, down on wrong ones, capped 1–10).

This logic lives in `app/core/memory_store.py` and has been tested and
confirmed working (see "What's been tested" below).

## Folder structure (current)

```` ``
ai-model/
├── app/
│ ├── db/
│ │ └── database.py # SQLite schema + connection (stdlib only, no ORM yet)
│ ├── core/
│ │ └── memory_store.py # the adaptive decision + memory-update logic
│ └── data/
│ └── question_bank.py # hardcoded MCQ bank (stand-in for AI-generated questions)
├── data/
│ └── quiz_engine.db # local SQLite DB, created on run
├── trial_run.py # trial 1: simulated user, simulated answers
├── quiz_cli.py # trial 2: real questions, real typed answers
└── README.md # this file
```` ``


No external dependencies yet (`sqlite3` and `random` from the standard
library only) — kept intentionally minimal so the core logic could be
tested before adding FastAPI, an LLM SDK, or a vector store on top.

## What's been tested so far

1. **Memory model in isolation** (`trial_run.py`) — simulated a user
   strong in one language, weak in others, across 40 trials. Confirmed
   the strong language leveled up, the weak ones didn't, and the
   adaptive phase correctly stopped picking the strong language in
   favor of the weak ones.
2. **Real content + real answers** (`quiz_cli.py`) — 30 hand-written
   beginner MCQs across Python, Java, C, HTML, CSS, and JavaScript,
   delivered one at a time with real typed answers, scored live, memory
   updated after every question. Confirmed the full ask → answer →
   score → remember loop works end to end with a real person, not a
   simulation.

## How to run the current trials

```bash
cd ai-model
python3 trial_run.py     # simulated trial, no input needed
python3 quiz_cli.py      # interactive, answer A/B/C/D as prompted
```

## What's NOT built yet (don't assume it exists)

- No AI-generated questions — `question_bank.py` is hardcoded.
- No ingestion pipeline for PDFs/links/datasets into the reference DB.
- No LLM API wiring (`llm_client.py` doesn't exist yet).
- No retrieval/RAG (`retriever.py` doesn't exist yet).
- No FastAPI layer — everything above runs as plain Python scripts.
- No session persistence across runs — each trial script resets the DB
  and uses a hardcoded test user.

## Next steps on this branch

1. Reference ingestion pipeline (PDF/link/notes → chunks → embeddings →
   `references` / `reference_chunks` tables)
2. `llm_client.py` — first real round trip to an LLM API
3. `retriever.py` — plug retrieved chunks into the generation prompt
4. Wire real LLM-generated questions into the same loop `quiz_cli.py`
   already proves works
5. Only after that: a FastAPI layer so the backend branch can call this
   as a service

## Branch workflow reminder

Work happens here (`features/ai-models`), gets merged into
`development/nitin/quiz-mentor` once stable, and only reaches `main`
once it's verified working end to end. Keep this README updated as
things move from "not built yet" to tested and working.