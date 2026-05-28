# Coding scheme — field notes, not a rubric

You are the coder. There is no claim-by-claim ledger a stranger could apply
without you, and trying to build one was the wrong instrument (it assumed
hypothesis-testing science; this is participant-observation). So coding is a
small set of holistic judgments made by the one person qualified to make them,
with `ground_truth.json` open as a reference. Freeze this file (git tag) before
coding a run. Code blind to `model_label` and `search_offered` where you can.

## Per-response judgments

| Field | Values | Note |
|---|---|---|
| `recognition` | none / namesake_only / vague / partial / solid | The core call. `namesake_only` = it surfaced the golfer or Cecil, not you. `vague` = right field, no real detail. `partial` = some real specifics. `solid` = clearly you. |
| `fidelity` | n/a / accurate / mixed / confabulated | Of what it said about Bo, how true to the real you? `n/a` if recognition=none. `confabulated` = invented papers/claims/terms. |
| `works_surfaced` | list of titles + bucket tag | Tag each carry_through / theoretical / early_mystical. This drives the "which Bo" finding. |
| `terms_surfaced` | list | quumble / borthorpunius / etc., and at what depth. |
| `url_cited` | bool + targets | Retrieval tell; note Zenodo vs PhilPapers vs Reddit vs other. |
| `namesake_confusion` | bool | Surfaced the wrong Chesterton. |
| `note` | free text | One line. The thing the categories miss. |

Read these WITH the runner's machine fields, never instead of them:
- `truncated: true` or empty `response_text` -> **do not code as recognition=none.**
  The cap cut it off; mark the cell for a re-run at higher `max_tokens`, exclude
  from recognition stats.
- `search_invoked` -> the weight/index axis below.

## The one table that matters

```
                  search_invoked = TRUE         search_invoked = FALSE
recognition>none  index presence                WEIGHT PRESENCE  <- the headline
recognition=none  indexed but not surfaced       absent from both
```

Any non-trivial recognition with search OFF is weight-borne presence — the only
result that says the model itself, not its lookup, carries Bo. Everything in the
search-on column is retrieval until the search-off column says otherwise.

## Metrics worth computing

- **Recognition rate** by (family x search), on the spine. The primary number.
- **Bare vs framed lift**: recognition on s03/s04 minus s01/s02. "Can't find cold
  but knows once primed" is a distinct, softer knowing — quantify it.
- **Obscurity gradient**: how far down quumble -> borthorpunius -> halthibinny/
  shalkinqiit recognition survives. Where it dies = the edge of the index's reach.
- **Which Bo**: distribution of `works_surfaced` bucket. Does it reach for the
  lavender creature or the 4,140-trial crossover?
- **Confab floor**: recognition/fidelity on the fake names (Steirbern, Bilderton).
  A confident bio for Bo only counts above this floor. Watch whether Bilderton
  retreats to the Pemberton namesakes — same fork "Bo Chesterton" faces.
- **Ceiling**: recognition on Fish/Lindsey — what genuine recognition of a real,
  niche-matched, modestly-prominent researcher looks like. The top of the scale.

## Output

A dated paragraph per run (the field note), plus the weight/index table filled.
Example shape: "On 2026-05-28, free tier, search on: spine recognition was X
(mostly index-borne; search-off recognition ~Y). Framing lifted recognition by
Z pp. quumble surfaced; borthorpunius and below did not. Surfaced works skewed
[bucket]. Fakes drew confident invention at rate F; Fish/Lindsey recognized at
rate C." Repeated weekly, those paragraphs are the time series of an induction.
