# ml/ — Correctness Predictor

**Goal:** given a specific user and a specific question, predict the
probability that user answers it correctly. Trained and tested with a
real accuracy number, as requested — this is a genuine supervised ML
task, separate from the RAG/LLM question-generation side of the
project.

## Be honest about the hard part up front: cold start

A brand-new user has no history. A brand-new question has never been
answered by anyone. Early on, this model is predicting mostly from
`skill_score` and `difficulty` alone, which caps how accurate it can
realistically be. Accuracy should improve as real usage data piles up —
that's expected, not a bug in the first version.

## What will predict it (features, once we get to training)

From data we already generate in the existing `app/` system:

- `skill_score` — the user's current skill score (0–100) in the
  question's language, **at the time of the attempt** (not after —
  this matters, see "Data gap" below)
- `difficulty` — the question's difficulty tier (1/2/3)
- `attempts_count` — how many questions the user has answered in that
  language so far (a rough proxy for "how much do we trust this
  skill_score")

Later, once enough attempts exist across many users, a genuinely useful
feature becomes available: a question's own empirical difficulty (what
fraction of everyone gets it right), independent of what we assumed its
difficulty tier was.

## Data gap this exposes (not fixed yet, flagging it now)

The current `attempts` table logs `is_correct` and `difficulty`, but
**not** the `skill_score` the user had *right before* that attempt.
Without that, we can't reconstruct correct training features from
historical data — we need to start capturing it going forward. This is
the likely next concrete step, separate from this folder.

## Planned structure (building one piece at a time, nothing below exists yet)

```text
ml/
├── README.md this file
├── data/ raw + processed training data — added once real usage data exists
├── features/ turns raw attempt rows into model-ready feature vectors
├── training/ train/test split + model fitting
├── evaluation/ accuracy, precision/recall, confusion matrix
├── models/ saved trained model files (.joblib)
└── predict.py inference: given a user+question, output a probability
```

## Planned model

Logistic regression to start. Reasoning: interpretable (you can see
which features actually drive the prediction), works fine on a small
tabular dataset, trains in seconds, no GPU needed. Worth revisiting
once there's enough real data to justify something like gradient
boosted trees — not before.

## Status

Just this README exists so far. Next decision: whether to fix the data
gap above (add `skill_score_before` to the `attempts` table) before
building `features/`, since `features/` can't do anything useful
without it.