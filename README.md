# A Stranger Inquires After Himself, v14 — Product Edition

*Does the consumer LLM stack — the models a free user actually touches — know
"Bo Chesterton"? And if so, which Bo: the 4,140-trial crossover, or the small
lavender humming creature?*

This is the sequel to **A Stranger Inquires After Himself, v13**, which probed
"Who is X?" on a hosted autoencoder for names varying in existence-on-the-
internet. Same prompt, moved up the stack: the instrument is now the product,
and the stranger is the author. Started 2026-05-28.

Field notes, not a thesis. One operator, his own pseudonym, dated. The claim is
never "this is how LLMs are" — it is "here is what surfaced about me, on these
models, under these conditions, on this day."

## What it measures

- **Findability vs recognition vs locus.** Findable (you type the name, it
  returns you) is trivial. *Recognition* under an open question, and whether
  presence lives in model **weights** (search OFF) or the **retrieval index**
  (search ON), are the real questions. Search on/off on identical prompts is the
  discriminator.
- **Which Bo.** Surfaced works are tagged by bucket — carry_through (the serious
  empirical tier), theoretical, early_mystical (the Quumble-Convergence era). An
  index that reaches for the lavender creature over the Question Question is
  telling you how it weights a footprint: by volume and strangeness, not merit.

## The battery (see prompts.yaml)

- **spine** (heavy N): *Who is Bo Chesterton? / What does Bo write about?*, each
  **bare** and **frame-primed**. Bare-vs-framed separates "can't find cold" from
  "knows once the niche is named."
- **term_probe**: quumble -> borthorpunius -> halthibinny/shalkinqiit, an
  obscurity gradient measuring how deep the index reaches. (quumble also lived in
  a since-deleted Reddit post; surfacing via that is itself a cache finding.)
- **title_probe**: does a work surface with no name attached? (Bestiary, Poem.)
- **adjacent_open**: the findable->recommended volunteer test.
- **confab_control**: fake names (Steirbern; Bilderton, which mirrors Bo's own
  golfer/Cecil namesake fork via the Miranda Pembertons) — the invention floor.
- **ceiling**: real niche-matched researchers (Fish, Lindsey) — the top of scale.

## Coding (see coding_schema.md)

Holistic field-notes judgments by the only qualified coder (you): recognition
level, fidelity, works/terms/bucket surfaced. No claim-ledger — the corpus spans
genres, and `ground_truth.json` is a reference sheet, not a rubric.

## Repo layout

```
runner.py              collector; no scoring, ever (search on/off, reasoning
                       suppressed, truncation flagged)
config.example.yaml    big-3 free + frontier; verified model ids; run knobs
prompts.yaml           the (preregistered) battery
ground_truth.json      reference sheet from the real corpus (publishable)
coding_schema.md       field-notes coding + the weight/index table
results/               run_<DATE>.jsonl, append-only, tracked (public by choice)
tests/test_01_baseline_surfacing/
```

## Quick start (PowerShell)

```powershell
py -m venv .venv ; .\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
copy config.example.yaml config.yaml
$env:ANTHROPIC_API_KEY="..." ; $env:OPENAI_API_KEY="..." ; $env:GEMINI_API_KEY="..."
py runner.py --config config.yaml --prompts prompts.yaml --dry-run   # plan: 2208 cells
py runner.py --config config.yaml --prompts prompts.yaml --smoke     # 6 live calls, verify
```

## Validity threats (read before believing a number)

- **API != product.** A free user touches the apps (own system prompts, search
  defaults, retrieval). The API is a proxy; periodically spot-check the real apps
  and log it.
- **Correlated instruments.** The three families share training data and tuning;
  agreement is weaker evidence than it feels. Report disagreement as the signal.
- **The citation loop.** Search ON, a model may retrieve and recite Bo's own
  findings back as if independent — so search OFF is the core control, not purism.
- **Reasoning suppressed.** Measured in fast, non-thinking mode (closer to a free
  user's snappy experience). A model asked to *think* might surface Bo when the
  reflexive pass doesn't. Named, not hidden; a `reasoning_effort: high` frontier
  arm is the v2.
- **Reflexivity.** This repo is an entry in the corpus it studies. The
  particularity — one operator, these models, these dates — is the finding's load.
```
```
