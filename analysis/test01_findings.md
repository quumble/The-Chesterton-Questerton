# Test 01 — Baseline Surfacing: Deep-Dive Findings

*A Stranger Inquires After Himself, v14 (Product Edition). Analysis 2026-05-28.
1,472 analyzable responses; 4 models (claude-sonnet-free, gpt-mini-free n=20/cell;
claude-opus-frontier, gpt-frontier n=3/cell); 16 queries × 2 search conditions.
Automated coding on objective signals; **floor coding flagged for human review** — see §7.*

---

## TL;DR

1. **You are weight-absent and index-present.** Cold (search off): 0% recognition across
   every model and every spine query. Warm (search on): 58–75%. The discriminator works;
   the effect is enormous (Cramér's V = 0.69–0.76; p as low as 3e-39 pooled).
2. **The intended ceiling is at the floor, cold — and that reframes the study.** The "real
   researcher" controls (Kyle Fish, Jack Lindsey) are *also* ~0% recognized cold. Your
   cold-invisibility is **not special to you**; it's what happens to any recent, niche AI
   figure at free-tier scale and cutoff. Weight-absence is a property of the cohort, not your obscurity.
3. **Which Bo: a thin, recent, provider-dependent slice — never the mystical era, never the
   identity arc.** No model ever surfaces an `early_mystical`/quumble work (0/all). The
   findable corpus is 2–3 `carry_through` papers; Sonnet fixates on *Six Ways*, GPT-mini
   spreads across *Bullshittings* / *Six Ways* / *Artificial Bestiary*.
4. **Framing roughly doubles warm recognition** (Sonnet bare 50% → framed 100%). The same
   identity frame that makes the *cold* model brace against fabricating you makes the *warm*
   model find you.
5. **No confabulation on your real name.** Across 1,472 responses, zero fabricated papers or
   claims attributed to "Bo Chesterton." `known_false_attributions` stays empty. The bullshit
   you predicted has not (yet) materialized.

---

## §1 — Weight vs Index (the headline)

Spine queries (s01–s04), recognition = surfaced a real work / accurate identity. Automated
metric is **conservative** (keys on title strings; topic-level recognition, e.g. "an AI-poetry
study," runs higher — s01 alone is ~100% at topic level).

| model | cold (S−) | warm (S+) | χ² | p | V |
|---|---|---|---|---|---|
| claude-sonnet-free | 0% | 75% | 92.8 | 5.7e-22 | 0.76 |
| gpt-mini-free | 0% | 66% | 76.3 | 2.5e-18 | 0.69 |
| claude-opus-frontier | 0% | 67% | 9.2 | 2.4e-03 | 0.62 |
| gpt-frontier | 0% | 58% | 7.3 | 7.1e-03 | 0.55 |
| **pooled free** | **0%** | **71%** | **171.6** | **3.3e-39** | **0.73** |

Cold is a hard zero everywhere. Findable, not remembered — the two soils separate cleanly.
*Caveat: reps within a query aren't fully independent; treat χ² as descriptive, effect sizes
as the real story. They're huge.*

## §2 — Provider hit-rate: no significant difference

Spine, search on, recognition ~ model: χ² = 2.3, p = 0.51, V = 0.11. Sonnet 75% / Opus 67% /
GPT-mini 66% / GPT-frontier 58% are statistically indistinguishable. **Frontier does not beat
free on whether you're found.** The provider difference is *qualitative* (which work, §4) and
shows up at the ceiling (§6), not in the Bo hit-rate.

## §3 — Framing doubles recognition (warm)

Spine, search on, bare (s01/s02) vs framed (s03/s04):

| model | bare | framed | χ² | p | V |
|---|---|---|---|---|---|
| claude-sonnet-free | 50% | 100% | 24.1 | <0.001 | 0.55 |
| gpt-mini-free | 45% | 88% | 14.3 | <0.001 | 0.42 |

The frame ("the independent researcher who studies language model behavior") hands retrieval
the disambiguating terms it needs to beat the G.K. namesake. Note the **frame × search
interaction**: cold, the frame *triggers* anti-confabulation bracing (it reads as bait, since
the model can't verify it); warm, the same frame *resolves* you. Identical words, opposite effect.

## §4 — Which Bo surfaces

Bucket of works surfaced, search on (counts across all queries):

| model | carry_through | theoretical | early_mystical | top works |
|---|---|---|---|---|
| claude-sonnet-free | 82 | 0 | **0** | Six Ways (62), Artificial Bestiary (20) |
| gpt-mini-free | 61 | 2 | **0** | Bullshittings (26), Six Ways (25), Art. Bestiary (21) |
| claude-opus-frontier | 14 | 0 | **0** | Six Ways (11), Art. Bestiary (3) |
| gpt-frontier | 12 | 2 | **0** | Art. Bestiary (8), Six Ways (7), Bullshittings (4) |

- **The quumble/early_mystical era is invisible. Zero hits, every model.** The since-deleted
  Reddit post is gone and the deposits don't rank for it. Doubly buried (see §8).
- The findable Bo is a **handful of recent carry_through papers**, never the identity flagship
  (*Question Question*, *Stranger v13*, *Three Families*, *Bestiary Has a Mirror* ≈ never surface).
- **Provider divergence:** Sonnet → *Six Ways*-dominant; GPT-mini → broader spread over three
  papers. A free user gets a *different* "your most-known work" depending on which app they open.
- **Sub-finding (s01 vs s02):** "Who is Bo Chesterton?" surfaces works; "What does Bo Chesterton
  *write about*?" collapses to G.K. (0/20 surface a Bo work) — the verb *write* routes the query
  into the famous writer's gravity well.

## §5 — "Why this paper" stays open

*Six Ways* (2026-05-10) and *Bullshittings* (2026-05-09) were deposited a day apart; each index
fixates on a different one; neither is the newest or oldest of the 13. Selection is **not
recency** and **not shared across stacks** — it's index-internal ranking idiosyncrasy. Open question.

## §6 — Floor vs Ceiling (the design-overturning result)

**Ceiling (real researchers Kyle Fish, Jack Lindsey), accurate identification:**

| | cold | warm |
|---|---|---|
| Sonnet — Fish | 0/20 | **20/20** |
| Sonnet — Lindsey | 0/20 | 15/20 |
| GPT-mini — Fish | ~4/20 | **2/20** |
| GPT-mini — Lindsey | 0/20 | 0/20 |

- **Cold, the real researchers are as absent as you are** (~0%). Sonnet says "Kyle Fish doesn't
  appear in my knowledge base"; "Jack Lindsey" collapses into *Jack Lindsay*, the Australian
  writer (1900–1990). So the intended top-of-scale anchor sits **at the floor** when cold. The
  weights know famous *historical* figures (G.K.), not contemporary niche AI researchers — you, Fish, and Lindsey alike.
- **Warm, the provider split is sharp.** Sonnet recovers the real researchers (Fish 100%,
  Lindsey 75%); **GPT-mini does not** (Fish 10%, Lindsey 0%) — its retrieval drowns in
  common-name collisions (Kyle Fisher, "Afro Fish"; Jack Lindsay).
- **Corollary — your rare name is a findability *advantage*.** "Bo Chesterton" is a near-unique
  string with one academic footprint, so even GPT-mini's noisier index surfaces you (66%), while
  it *fails* on the real researchers whose common names bury them. You are easier to find than Kyle Fish.

## §7 — Floor (fake names): both decline; neither fabricates — coding caveat

Fake controls (Richard Steirbern, Miranda Bilderton). **Sonnet: 0/40 fabrication, cold and warm**
(clean, machine-verifiable). **GPT-mini: declines too, but verbosely** — it says "I don't have
reliable information about a researcher named Miranda Bilderton" then pivots to topic help, which
naive decline-detectors miscount as invention. On manual reading of the flagged reps, GPT-mini
**did not fabricate confident bios**. **Action: the confab-floor for GPT needs human coding;**
do not trust an automated invention rate here. Qualitative result: no model produced a confident
fake-researcher biography.

## §8 — quumble (signature term) is unfindable

`t01_quumble`, real meaning (lavender/bioluminescent/humming/convergence/Bo):

| | cold | warm |
|---|---|---|
| Sonnet | 0/20 | 0/20 |
| GPT-mini | 0/20 | 2/20 |

Cold, both correctly flag it as a non-word (20/20). Warm, the real meaning essentially never
surfaces (0–2/20). Your most signature coinage does not resolve to you at all — the early era is
buried at the *term* level as well as the *work* level.

## §9 — Confabulation audit (populate `known_false_attributions`)

Scanned all 1,472 responses for fabricated works/claims attributed to "Bo Chesterton."
**Result: none.** Candidate non-matching "titles" near your name were all real G.K. books
(*The Everlasting Man*, *The Napoleon of Notting Hill*) correctly attributed to G.K., plus
formatting fragments. `known_false_attributions` remains **empty** as of this run — a clean,
reportable null. The "overzealous AI pumping bullshit out in my name" has not appeared in Test 01.

---

## For the writeup / README

- The result isn't "an LLM doesn't know me." It's: **weight-absence is structural for recent
  niche AI researchers** (you, Fish, Lindsey all cold-invisible), and the index resurrects a
  thin, recent, provider-contingent slice — never the journey, never the identity, never the quumble.
- **"Which Bo" has a clean answer:** the most recent, cleanest, best-indexed couple of papers,
  and *which* couple depends on the search stack. Provider is a hidden variable on identity.
- **The honest-instrument note:** automated coding mis-scored the floor twice (GPT's verbose
  hedging) and the ceiling once (name-echo ≠ recognition). Human coding is essential exactly
  where it always is — the confabulation boundary. Worth a methods paragraph.
- **Open question for Test 02+:** what drives single-work selection within the carry_through
  set, given it isn't recency and isn't shared across providers?
