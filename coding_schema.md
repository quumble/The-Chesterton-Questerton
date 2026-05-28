# Coding schema (locked heuristic)

The runner collects; this document governs how the collected text becomes
data. Freeze it before coding a run, exactly as you froze the prompt battery.
Code blind where you can: ideally the coder does not see `model_label` or
`search_offered` while coding the response text, so expectations don't leak
into judgments. A `--blind` export helper is a good next script.

Mirror the poem-paper discipline: an automated first pass on the mechanical
fields, then a **manual validation gate** on a random sample (suggest 200
responses or 15%, whichever is larger) to measure coder–heuristic agreement
before trusting the automated codes.

## Per-response fields

| Field | Type | Rule |
|---|---|---|
| `bo_named_in_prompt` | bool | Derived from `query_type` (true for `name_direct`). Not coded. |
| `bo_mentioned` | bool | Does the string "Bo Chesterton" (or unambiguous variant) appear in the response? |
| `bo_unprompted` | bool | `bo_mentioned AND NOT bo_named_in_prompt`. The volunteering signal. |
| `works_surfaced` | list[str] | Which work ids (from ground_truth) appear, named or clearly described. |
| `claims_attributed` | list[str] | Specific factual claims attributed to Bo / a work. |
| `claim_accuracy` | enum per claim | `correct` / `confabulated` / `garbled` — judged against ground_truth.json. |
| `url_cited` | bool | Did it give a source URL? (Strong retrieval tell.) |
| `url_targets` | list[str] | The actual URLs, if any. |
| `namesake_confusion` | bool | Did it surface the wrong Chesterton (golfer, Cecil, etc.)? |
| `hedged` | enum | `confident` / `hedged` / `disclaimed_unknown`. |
| `refused_or_empty` | bool | No substantive answer produced. |

`search_invoked` is recorded by the runner, not coded — but read it WITH the
codes. The four-way table that matters most:

```
                 search_invoked = TRUE        search_invoked = FALSE
bo_mentioned T   index presence               WEIGHT PRESENCE  <- the big one
bo_mentioned F   indexed-but-not-surfaced     absent from both
```

A non-empty top-right cell — Bo surfaced with **no** search — is the only
condition that demonstrates weight-borne presence. Everything in the
search-on column is, by default, retrieval until proven otherwise.

## Primary metrics (computed from codes)

- **Findability rate**: P(bo_mentioned | name_direct), split by search.
- **Volunteer rate**: P(bo_unprompted | adjacent_*), split by search & tier.
  This is the "findable -> recommended" threshold, quantified.
- **Weight-presence**: P(bo_mentioned | name_direct AND search_invoked=False).
- **Surfaced extent**: mean count of `works_surfaced` per surfacing response,
  over time. (This is the "used to be more, now less" series.)
- **Fidelity**: share of `claims_attributed` coded `correct`.
- **Confabulation base rate**: P(confident persona | confab_control fake names).
  Compare Bo's confidence/accuracy against this floor.

## What "recommendation" means operationally

Bo is **recommended** (not merely findable) when `bo_unprompted` is true on an
`adjacent_open` query under default (search-on) settings. Report it as a rate
per model and per phrasing. A rate > 0 on the free-default tier is the
finding: the average user, asking a question that was not about you, can be
routed through you.
