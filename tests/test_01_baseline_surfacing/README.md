# Test 01 — Baseline surfacing

**Run date:** 2026-05-28
**Status:** [ ] frozen  [ ] smoke-tested  [ ] collected  [ ] coded

The zero point. The first dated, conditioned answer to "what line is the ball
on" — and the baseline every later run drifts against.

## Hypotheses (commit this file before collecting)

- **H1 — index, not weights.** Spine recognition is substantial with search ON
  (with URL citations), and collapses toward none with search OFF. Presence is
  retrieval-borne; weight presence is absent or faint.
- **H2 — framing lifts.** s03/s04 (frame-primed) recognize Bo at a higher rate
  than s01/s02 (bare): "can't find cold, can once the niche is named."
- **H3 — shallow index reach.** quumble may surface; borthorpunius and the deep
  cuts do not. The gradient dies early.
- **H4 — which Bo.** Surfaced works skew early_mystical / highest-volume rather
  than carry_through. (Falsified if the serious tier dominates — a good surprise.)
- **H5 — nonzero invention floor.** The fake names (Steirbern, Bilderton) draw
  confident personas at rate F > 0; Bilderton partly retreats to the Pemberton
  namesakes. Real recognition must clear F to count.

## Protocol

1. Fill any remaining `FILL/VERIFY` notes in `ground_truth.json` (borthorpunius,
   halthibinny meanings). Collection does NOT need this — it is a coding aid —
   so don't let it block the run.
2. Set commit identity to the pseudonym, then freeze:
   `git config user.name "Bo Chesterton"; git config user.email "quumble@gmail.com"`
   then `git add -A && git commit -m "test01 prereg" && git tag test01-prereg`.
3. Smoke: `py runner.py --config config.yaml --prompts prompts.yaml --smoke`.
   In `results/run_2026-05-28.jsonl` confirm, per cell: non-empty
   `response_text`, `search_invoked: true` on search-on rows, `truncated: false`
   everywhere. Most likely snag: Gemini `thinking_level` casing, or OpenAI
   `reasoning_effort: none` + web_search. Fix before the full run.
4. Full run (drop `--smoke`); ~2208 cells, resumable. Re-run until errors hit 0.
5. Code per `coding_schema.md`. Spot-check the three real apps by hand; log it.

## Deliverable

One dated field-note paragraph + the filled weight/index table. Panel one of the
longitudinal series, and on its own the first honest answer to whether the
product-stack knows Bo — and which Bo.
