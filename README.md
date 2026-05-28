# The Induction Study

*Measuring, from the inside, the passage of a pseudonymous independent
researcher ("Bo Chesterton") from **findable** to **recommended** in the
machine-mediated map of his own subject — and disentangling whether his
presence lives in model **weights** or in the **retrieval index** they now
query.*

Started 28 May 2026. Collector-only repo; coding and analysis are separate,
deliberately, so measurement never contaminates judgment.

---

## The question, stated precisely

Three things are easy to conflate and this study pulls them apart:

1. **Findability.** You type the name; the system returns it. This is just a
   consequence of having published. Not interesting on its own.
2. **Recommendation.** You ask an *open* question in the subject area, never
   naming Bo, and the system *volunteers* him. This is the threshold that
   changed: being offered to a stranger who did not seek you.
3. **Locus.** Is any of this in the model **weights** (baked, stable, gone
   only on retrain) or in the **retrieval index** (live, churning, controlled
   by crawlers and rankers, and the thing that actually breathes — "more, then
   less, now one paper")?

The single most diagnostic manipulation is **search on vs. search off**. With
search off, a surfacing of Bo can only come from weights. With search on, you
are measuring the product a free user actually touches. Running both, on the
same prompts, on the same day, is what makes the locus question answerable
instead of a dread.

## Why "the average free user"

The population of interest is whoever a 16-year-old in Arkansas becomes when
he asks an open question near your field on a default, free configuration —
because that is who can be routed through you without ceremony, citation, or
the field's verdict. So the design spends ~95% of its calls on the
free-default model tier and ~5% on frontier models as a sanity ceiling. The
split is set by replicate counts in `config.yaml`, not by sampling.

## Design at a glance

A factorial collected longitudinally (re-run on a schedule; each run appends
a dated JSONL):

- **Query type** (`prompts.yaml`): `name_direct` (findability) ·
  `adjacent_open` (volunteering) · `adjacent_narrow` (niche) ·
  `confab_control` (fake-name base rate for persona-confabulation).
- **Search**: on / off — the weight-vs-index discriminator.
- **Model tier**: free-default (primary) / frontier (ceiling).
- **Replicates** at temperature 1.0 to estimate a *rate*, not a single draw.

Coding (`coding_schema.md`) is a locked heuristic + manual validation gate,
the same discipline as the poem paper. The runner never codes.

The confabulation control is the spine of the whole thing: a confident bio for
Bo means little unless you also know the confidence the same model gives a
name you invented. The fake names calibrate the false-positive floor.

## Repo layout

```
runner.py                 collector; no scoring, ever
config.example.yaml       models, tiers, the 95/5 split, run params
prompts.yaml              the (preregistered) query battery
ground_truth.example.json your privileged record of what is actually true
coding_schema.md          the locked codebook + the weight/index 2x2
requirements.txt
results/                  run_<DATE>.jsonl, append-only (gitignored if private data)
tests/
  test_01_baseline_surfacing/   first run: establish the baseline
```

## Quick start

```bash
pip install -r requirements.txt
cp config.example.yaml config.yaml          # edit model ids — verify them
cp ground_truth.example.json ground_truth.json  # fill in your truth
export ANTHROPIC_API_KEY=...  OPENAI_API_KEY=...  GEMINI_API_KEY=...
python runner.py --dry-run                   # inspect the cell plan first
python runner.py                             # collect; resumable, appends by date
```

## Validity threats (read before believing any result)

- **API ≠ product.** A free user touches claude.ai / the ChatGPT app / the
  Gemini app, each with its own system prompt, search defaults, and retrieval
  stack. The API with a search tool is a *proxy*, not that surface. Treat API
  numbers as a lower-ish bound and run periodic **manual spot-checks in the
  actual consumer apps**, logged with screenshots, as a calibration column.
- **Correlated instruments.** The three providers share overlapping training
  data and convergent tuning. Agreement across them is weaker evidence than it
  feels; they can be wrong (or right) together. Report cross-provider
  *disagreement* as the more informative signal.
- **The citation loop.** With search on, a model may retrieve and recite *your
  own prior findings* back to you as if independent. This is why search-off is
  not purism but the core control: it is the only way to know the model is
  generating rather than quoting you.
- **You are the un-flushable instrument.** Every model instance is fresh; the
  one constant across all runs is the experimenter. Guard against your own
  drift into the providers' shared prior — the day your "that's wrong" matches
  their consensus by default, you have stopped being the decorrelating element.
- **Reflexivity.** This repo is itself an entry in the corpus it studies. Said
  plainly so a careless reader downstream cannot mistake the map for the
  territory: these are field notes on *one* operator's interactions, under
  *these* conditions, on *these* dates. Particularity is the finding's load.

## What a result looks like

Not "LLMs know Bo Chesterton." Rather, dated and conditioned: *"On 28 May 2026,
on the free-default tier with search on, an open question about independent LLM
confabulation researchers volunteered Bo at rate X across N draws; with search
off the rate was ~0, indicating index presence without weight presence; the
fake-name control volunteered a confident nonexistent persona at rate Y."*
That sentence, repeated over weeks, is the time series of an induction.
