# Quiz Mentor

**An AI-powered quiz platform that actually adapts to you** — not a static
question bank, a mentor that learns what you're weak at and focuses there.

## The problem

Most coding quiz sites give everyone the same questions regardless of
skill. A beginner in Python gets steamrolled by the same quiz an expert
gets; an expert gets bored repeating basics they already know. Almost
none of them track your ability *across multiple languages at once* and
use that to decide what to ask you next.

## What Quiz Mentor does

1. **Profiles you first.** Your first ~30 questions are beginner-level,
   spread randomly across every supported language (Python, Java, C,
   HTML, CSS, JavaScript, and growing). This builds a picture of where
   you're strong and where you're not, without assuming anything upfront.
2. **Adapts after that.** Once your profile exists, Quiz Mentor starts
   asking more questions in your *weaker* languages, and raises the
   difficulty as you prove you're ready — like a tutor who notices you're
   solid in Python but shaky in C, and adjusts the session accordingly.
3. **Draws on real reference material.** Questions aren't just generated
   from nothing — they're grounded in uploaded books, docs, past papers,
   and datasets, so the content stays accurate and can keep growing as
   more material is added.

## Why it's useful

- **Students** get practice that targets their actual gaps instead of
  reviewing what they already know.
- **Job seekers / interview prep** get a quiz that gets harder as they
  improve, instead of staying static.
- **Self-taught developers** get an honest signal on which languages
  need more attention, across their whole skill set rather than one at
  a time.

## How it works (high level)
```text
Frontend ──────────────▶ Backend ──────────────▶ AI-Engine
▲ │ │
│ │ stores results │ generates next
│ ▼ │ question using:
│ User/Attempt DB ┌─────────┴─────────┐
│ │ Reference DB │
│ │ (books/PDFs/links)│
│ │ + │
│ │ LLM (question │
│ │ generation) │
│ └─────────┬─────────┘
└────────────────────────────────────────────────────────┘
```

The **Backend** owns users, sessions, and auth (Firebase). The
**AI-Engine** owns deciding what to ask and generating it, using a
combination of a per-user skill memory and reference material via
retrieval-augmented generation (RAG) — no model is trained from scratch;
it's prompting an LLM with the right context each time, which is what
keeps it able to incorporate new uploaded material immediately.

## Project status

Early-stage, actively being prototyped. Target for the first working
version (VR1) is **mid-December**. The AI-engine's core decision logic
and a basic question-delivery loop are built and tested; question
generation via LLM, the reference ingestion pipeline, and the backend/
frontend integration are in progress.

## Branch structure

features/ai-models → all AI-engine development
development/... → integration of AI-engine + backend + frontend work
main → stable, working releases only


Work starts in a feature branch, merges into `development` once it's
stable, and only reaches `main` once it's verified working end to end.
Backend and frontend will get their own feature branches following the
same pattern as the project grows.

## Contributing / getting started

See the README on the `features/ai-models` branch for how the AI-engine
is structured and how to run its current test scripts.
