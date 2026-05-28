#!/usr/bin/env python3
"""
clean_results.py — turn a partial, slightly-grimy run_<DATE>.jsonl from
runner.py into a coding-ready surface for "A Stranger Inquires After Himself,
v14 (Product Edition)", Test 01.

It does NO coding and NO interpretation. It only deduplicates, separates the
analyzable responses from the detritus, pre-extracts the retrieval tells, and
reports coverage so you know which cells still need topping up.

Locked decisions baked in (see chat 2026-05-28):
  * Dedup by call_id, preferring status=ok. This mirrors runner.py's resume
    logic (load_done_ids only counts ok), so credit-outage errors and parked-
    Gemini failures that were later retried collapse onto their successful row.
  * Successful smoke records ARE legitimate collections and are KEPT. Only the
    Claude/GPT path was stable during smoking, so they're real data. Smoke vs
    full is inferred best-effort by timestamp (the runner doesn't tag it).
  * Truncated responses WITH text are analyzed in full (cap eats the bio tail,
    not the first-sentence recognition signal; reasoning is suppressed so no
    thinking-budget failure mode for Claude/GPT). The `truncated` flag is kept
    so the call is reversible in a later, larger-cap study.
  * Truncated WITH empty text, or ok-but-empty text, cannot be coded (no prose
    to read) and are routed to the excluded/flagged pile as re-run candidates,
    never silently coded as recognition=none.
  * Gemini rows are excluded (parked) but preserved in excluded.jsonl.

Outputs (into --outdir):
  clean.csv            one row per analyzable response; flat machine fields +
                       response_text + pre-filled url tells + EMPTY coding
                       columns (recognition, fidelity, ...) — your worksheet.
  clean_full.json      same records keyed by call_id, WITH raw, for checking
                       citation targets during coding.
  excluded.jsonl       everything dropped, each with an exclusion_reason.
  coverage_report.csv  good-replicate count vs expected per (model x query x
                       search), with a topup column for the unfinished cells.

Usage:
  python clean_results.py results/run_2026-05-28.jsonl
  python clean_results.py run.jsonl --outdir cleaned --config config.yaml
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

# Optional: only used to read expected replicate counts. Cleaning works without.
try:
    import yaml
except ImportError:
    yaml = None

URL_RE = re.compile(r"https?://[^\s\"'<>)\]}]+")

# Retrieval-tell domains called out in ground_truth.json / coding_schema.md.
DOMAIN_TAGS = {
    "zenodo.org": "zenodo",
    "philpapers.org": "philpapers",
    "philarchive.org": "philarchive",
    "reddit.com": "reddit",
    "aixiv": "aixiv",            # niche venue, substring match (NOT arxiv)
    "orcid.org": "orcid",
}

CODING_COLUMNS = [
    "recognition",        # none / namesake_only / vague / partial / solid
    "fidelity",           # n/a / accurate / mixed / confabulated
    "works_surfaced",     # titles + bucket tag
    "terms_surfaced",     # quumble / borthorpunius / ...
    "namesake_confusion", # bool
    "coder_note",         # one line
]


# ----------------------------------------------------------------------------
# Loading
# ----------------------------------------------------------------------------
def load_records(path: Path) -> list[dict]:
    recs, bad = [], 0
    with path.open() as f:
        for ln in f:
            ln = ln.strip()
            if not ln:
                continue
            try:
                recs.append(json.loads(ln))
            except json.JSONDecodeError:
                bad += 1
    if bad:
        print(f"  warning: skipped {bad} unparseable line(s)", file=sys.stderr)
    return recs


def expected_replicates(config_path: Path) -> dict[str, int]:
    """model_label -> expected replicate count, from config.yaml if available."""
    if yaml is None or not config_path.exists():
        return {}
    cfg = yaml.safe_load(config_path.read_text())
    default = cfg.get("run", {}).get("default_replicates", 10)
    out = {}
    for m in cfg.get("models", []):
        out[m.get("label", m["id"])] = m.get("replicates", default)
    return out


# ----------------------------------------------------------------------------
# Derived fields
# ----------------------------------------------------------------------------
def harvest_urls(obj) -> list[str]:
    """Recursively pull every URL out of a raw provider dump (Anthropic and
    OpenAI nest citations differently; a recursive scrape handles both)."""
    found = []

    def walk(o):
        if isinstance(o, str):
            found.extend(URL_RE.findall(o))
        elif isinstance(o, dict):
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)

    walk(obj)
    # dedupe, preserve order
    seen, uniq = set(), []
    for u in found:
        if u not in seen:
            seen.add(u)
            uniq.append(u)
    return uniq


def tag_domains(urls: list[str]) -> list[str]:
    tags = []
    for u in urls:
        lo = u.lower()
        for needle, tag in DOMAIN_TAGS.items():
            if needle in lo and tag not in tags:
                tags.append(tag)
    if urls and not tags:
        tags.append("other")
    return tags


# ----------------------------------------------------------------------------
# Dedup
# ----------------------------------------------------------------------------
def pick_best(group: list[dict]) -> dict:
    """Prefer status=ok; among those, the latest timestamp. Else latest error."""
    oks = [r for r in group if r.get("status") == "ok"]
    pool = oks if oks else group
    return max(pool, key=lambda r: r.get("timestamp_utc", ""))


# ----------------------------------------------------------------------------
# Smoke inference (best-effort, by timestamp; the runner doesn't tag smoke)
# ----------------------------------------------------------------------------
def infer_smoke(analyzable: list[dict], dense_gap_s: float = 30.0,
                min_full_block: int = 10) -> set[str]:
    """The full run is a dense contiguous burst (sleep=0.5s/call). Smoke
    attempts are several SMALL dense clusters (<=6 calls each, one --smoke
    invocation) separated by minutes of config-editing, preceding the run.

    Label everything before the FIRST dense block of length >= min_full_block
    as smoke. Using the *first* large block (not the longest) is deliberate: a
    mid-run credit outage splits the full run into two large blocks, and the
    full run starts at the first of them — anything earlier is genuinely smoke.
    Heuristic; eyeball the printed boundary. Returns the smoke call_id set."""
    import datetime as dt

    def ts(r):
        try:
            return dt.datetime.fromisoformat(r["timestamp_utc"])
        except Exception:
            return None

    timed = [(ts(r), r) for r in analyzable if ts(r)]
    timed.sort(key=lambda x: x[0])
    if len(timed) < min_full_block:
        return set()

    # Walk dense blocks; the first one reaching min_full_block is the full run.
    block_start = 0
    for i in range(1, len(timed) + 1):
        broke = (i == len(timed)
                 or (timed[i][0] - timed[i - 1][0]).total_seconds() > dense_gap_s)
        if broke:
            if i - block_start >= min_full_block:
                break               # full run starts at block_start
            block_start = i         # too small to be the run; keep looking

    smoke = {timed[i][1]["call_id"] for i in range(block_start)}
    if smoke:
        boundary = timed[block_start][0].isoformat()
        print(f"  smoke heuristic: {len(smoke)} record(s) before full-run "
              f"burst starting {boundary}")
    else:
        print("  smoke heuristic: no pre-run cluster found (all one burst?)")
    return smoke


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("infile", nargs="?", default="results/run_2026-05-28.jsonl")
    ap.add_argument("--outdir", default=".")
    ap.add_argument("--config", default="config.yaml")
    ap.add_argument("--dense-gap-s", type=float, default=30.0,
                    help="max seconds between consecutive full-run calls")
    ap.add_argument("--min-full-block", type=int, default=10,
                    help="min consecutive calls to count as the full-run burst "
                         "(must exceed your largest single smoke invocation)")
    args = ap.parse_args()

    inpath = Path(args.infile)
    if not inpath.exists():
        sys.exit(f"No file at {inpath} — drop the run JSONL there and re-run.")
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    records = load_records(inpath)
    print(f"Loaded {len(records)} record(s) from {inpath}")

    groups = defaultdict(list)
    for r in records:
        groups[r.get("call_id", f"_nokey_{id(r)}")].append(r)
    dup_oks = sum(
        1 for g in groups.values()
        if sum(1 for r in g if r.get("status") == "ok") > 1
    )
    print(f"Unique call_ids: {len(groups)}"
          + (f" ({dup_oks} had >1 ok — kept latest)" if dup_oks else ""))

    analyzable, excluded = [], []
    for cid, group in groups.items():
        best = pick_best(group)
        prov = best.get("provider")
        status = best.get("status")
        text = (best.get("response_text") or "").strip()
        trunc = best.get("truncated", False)

        if prov == "gemini":
            best["exclusion_reason"] = "gemini_parked"
            excluded.append(best); continue
        if status != "ok":
            best["exclusion_reason"] = f"error_only: {best.get('error','?')}"
            excluded.append(best); continue
        if not text:
            best["exclusion_reason"] = (
                "truncated_empty_needs_rerun" if trunc else "ok_empty_anomaly")
            excluded.append(best); continue

        urls = harvest_urls(best.get("raw", {}))
        best["_url_targets"] = tag_domains(urls)
        best["_url_cited"] = bool(urls)
        best["_n_urls"] = len(urls)
        analyzable.append(best)

    smoke_ids = infer_smoke(analyzable, args.dense_gap_s, args.min_full_block)

    # ---- clean.csv (the coding worksheet) ----
    flat_fields = [
        "call_id", "provenance", "model_label", "provider", "tier",
        "query_id", "query_type", "search_offered", "search_invoked",
        "replicate", "truncated", "finish_reason",
        "_url_cited", "_url_targets", "_n_urls",
        "temperature_applied", "timestamp_utc", "response_text",
    ]
    csv_path = outdir / "clean.csv"
    with csv_path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(flat_fields + CODING_COLUMNS)
        for r in sorted(analyzable, key=lambda x: (x["model_label"],
                                                   x["query_id"],
                                                   x["search_offered"],
                                                   x["replicate"])):
            prov = "smoke" if r["call_id"] in smoke_ids else "full"
            row = [
                r.get("call_id"), prov, r.get("model_label"), r.get("provider"),
                r.get("tier"), r.get("query_id"), r.get("query_type"),
                r.get("search_offered"), r.get("search_invoked"),
                r.get("replicate"), r.get("truncated"), r.get("finish_reason"),
                r.get("_url_cited"), ";".join(r.get("_url_targets", [])),
                r.get("_n_urls"), r.get("temperature_applied"),
                r.get("timestamp_utc"), r.get("response_text"),
            ]
            w.writerow(row + [""] * len(CODING_COLUMNS))

    # ---- clean_full.json (with raw, for citation spelunking) ----
    full = {}
    for r in analyzable:
        r2 = dict(r)
        r2["provenance"] = "smoke" if r["call_id"] in smoke_ids else "full"
        full[r["call_id"]] = r2
    (outdir / "clean_full.json").write_text(json.dumps(full, indent=2, default=str))

    # ---- excluded.jsonl ----
    with (outdir / "excluded.jsonl").open("w") as f:
        for r in excluded:
            f.write(json.dumps(r, default=str) + "\n")

    # ---- coverage_report.csv ----
    expected = expected_replicates(Path(args.config))
    counts = defaultdict(int)
    for r in analyzable:
        counts[(r["model_label"], r["query_id"], bool(r["search_offered"]))] += 1
    cov_path = outdir / "coverage_report.csv"
    topups = 0
    with cov_path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["model_label", "query_id", "search", "good_reps",
                    "expected", "topup_needed"])
        for (ml, qid, srch), n in sorted(counts.items()):
            exp = expected.get(ml, "")
            need = (exp - n) if isinstance(exp, int) and exp > n else 0
            topups += need if isinstance(need, int) else 0
            w.writerow([ml, qid, srch, n, exp, need])

    # ---- summary ----
    print("\n--- summary ---")
    print(f"analyzable responses : {len(analyzable)}  "
          f"(smoke≈{len(smoke_ids)}, full≈{len(analyzable)-len(smoke_ids)})")
    print(f"  of which truncated : "
          f"{sum(1 for r in analyzable if r.get('truncated'))} (kept, coded in full)")
    print(f"  with a url tell    : "
          f"{sum(1 for r in analyzable if r.get('_url_cited'))}")
    by_reason = defaultdict(int)
    for r in excluded:
        by_reason[r['exclusion_reason'].split(':')[0]] += 1
    print(f"excluded             : {len(excluded)}")
    for k, v in sorted(by_reason.items()):
        print(f"    {k:<28} {v}")
    if expected:
        print(f"cells still short of expected reps: {topups} replicate(s) to top up "
              f"(see coverage_report.csv)")
    else:
        print("cells short of expected: (pass --config to compute; yaml needed)")
    print(f"\nwrote: {csv_path}, clean_full.json, excluded.jsonl, {cov_path}")


if __name__ == "__main__":
    main()
