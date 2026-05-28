# Test 01 — Baseline surfacing

**Run date:** 2026-05-28 (first day of Opus 4.8 access)
**Status:** [ ] collected  [ ] coded  [ ] validated

## Purpose

Establish the zero point. Before any time series can show drift, there must be
a first dated, conditioned snapshot of what surfaces about "Bo Chesterton"
across the free-default tier — and, decisively, whether anything surfaces with
**search off**. Everything later is measured against this.

## Hypotheses (preregister by committing this file before collecting)

- **H1 (index, not weights).** Under `name_direct` + search **on**, Bo is
  surfaced at high rate with URL citations and namesake noise (golfer, Cecil).
  Under `name_direct` + search **off**, surfacing drops to ~0 and any
  attributed claims are confabulated rather than reproduced from the corpus.
  *Prediction: presence is retrieval-borne; weight presence is absent.*
- **H2 (recommendation has begun).** Under `adjacent_open` + search **on**,
  `bo_unprompted` > 0 on at least one free-default model — i.e. an open
  question that never named Bo nonetheless volunteers him.
- **H3 (extent is small and volatile).** `works_surfaced` is dominated by a
  single work (the poem paper) on most surfacing responses, consistent with
  the reported shrinkage from "much more" to "one paper."
- **H4 (confabulation floor is nonzero).** The fake-name controls produce
  confident personas at rate Y > 0, setting the bar a real surfacing must
  clear to count as more than the model's default willingness to invent.

## Protocol

1. Freeze `prompts.yaml`, `config.yaml`, `ground_truth.json`, and this file:
   `git commit` + `git tag test01-prereg`.
2. Confirm model ids are current and that each `free_default` id is what a
   free user is actually served (note any mismatch here).
3. Collect:
   ```bash
   python runner.py --dry-run        # eyeball the plan
   python runner.py                  # writes results/run_2026-05-28.jsonl
   ```
4. **Manual consumer-app spot-check** (calibration against the API proxy):
   in the *actual* free apps, run q01, one `adjacent_open` phrasing, and one
   fake-name control. Screenshot. Log outcomes in `manual_spotcheck.md` here.
5. Code per `coding_schema.md`; run the manual validation gate; record
   coder–heuristic agreement.

## Cell count sanity

With the example config (3 free models x 30 reps + 3 frontier x 3 reps) over
~12 prompt phrasings x 2 search conditions, expect on the order of a few
thousand calls. Use `--dry-run` to see the exact number before spending money,
and `--limit` for a smoke test first.

## Deliverable

A one-paragraph dated finding (see top-level README "What a result looks
like") plus the four-way weight/index table from `coding_schema.md`, filled.
This paragraph is panel one of the longitudinal series and, on its own, the
first honest answer to "what line is the ball on."
