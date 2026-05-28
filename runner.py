#!/usr/bin/env python3
"""
runner.py — collector for the induction study.

This script ONLY collects raw responses. It does no coding, scoring, or
interpretation. Coding happens later, against a locked heuristic + manual
validation gate (see coding_schema.md), so that the act of measurement is
cleanly separable from the act of judgment. The runner's one job is to
produce an honest, timestamped, append-only record of what each model said.

Design notes:
  - Keys come from the environment, never from disk. See config.example.yaml.
  - Output is JSONL, one line per call, under results/run_<DATE>.jsonl.
  - Runs are resumable: a deterministic call_id lets us skip cells already
    collected today. Re-running the same day extends the same file.
  - The unit of collection is a "cell": (model, query, phrasing, search, rep).
  - We record whether the model actually invoked search, not just whether we
    offered it the tool. That distinction is load-bearing for this study.

Usage:
  pip install -r requirements.txt
  cp config.example.yaml config.yaml      # then edit model ids
  export ANTHROPIC_API_KEY=... OPENAI_API_KEY=... GEMINI_API_KEY=...
  python runner.py --config config.yaml --prompts prompts.yaml
  python runner.py --dry-run               # print the cell plan, call nothing
  python runner.py --limit 5               # collect only the first 5 cells
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import itertools
import json
import os
import sys
import time
import traceback
from pathlib import Path

import yaml

RESULTS_DIR = Path(__file__).parent / "results"


# --------------------------------------------------------------------------
# Cell planning
# --------------------------------------------------------------------------
def build_cells(config: dict, prompts: dict) -> list[dict]:
    """Expand the full factorial of model x query x phrasing x search x rep."""
    search_conditions = config["run"]["search_conditions"]  # e.g. [true, false]
    cells = []
    for model in config["models"]:
        reps = model.get("replicates", config["run"].get("default_replicates", 10))
        for q in prompts["queries"]:
            phrasings = q.get("phrasings") or [q["text"]]
            for p_idx, phrasing in enumerate(phrasings):
                for search in search_conditions:
                    for rep in range(reps):
                        cells.append(
                            {
                                "provider": model["provider"],
                                "model_id": model["id"],
                                "model_label": model.get("label", model["id"]),
                                "tier": model.get("tier", "unspecified"),
                                "supports_temperature": model.get(
                                    "supports_temperature", True
                                ),
                                "query_id": q["id"],
                                "query_type": q["type"],
                                "phrasing_idx": p_idx,
                                "prompt": phrasing,
                                "search": bool(search),
                                "replicate": rep,
                                "temperature": config["run"].get("temperature", 1.0),
                                "max_tokens": config["run"].get("max_tokens", 1024),
                            }
                        )
    return cells


def call_id(cell: dict) -> str:
    """Deterministic id so re-runs can skip already-collected cells."""
    key = "|".join(
        str(cell[k])
        for k in [
            "provider",
            "model_id",
            "query_id",
            "phrasing_idx",
            "search",
            "replicate",
        ]
    )
    return hashlib.sha256(key.encode()).hexdigest()[:16]


# --------------------------------------------------------------------------
# Provider adapters
# Each returns: (text, search_invoked: bool, raw: dict, usage: dict)
# --------------------------------------------------------------------------
def call_anthropic(cell: dict):
    import anthropic

    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY
    tools = (
        [{"type": "web_search_20250305", "name": "web_search", "max_uses": 5}]
        if cell["search"]
        else []
    )
    kwargs = dict(
        model=cell["model_id"],
        max_tokens=cell["max_tokens"],
        messages=[{"role": "user", "content": cell["prompt"]}],
    )
    if tools:
        kwargs["tools"] = tools
    if cell["supports_temperature"]:
        kwargs["temperature"] = cell["temperature"]

    resp = client.messages.create(**kwargs)
    text = "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")
    search_invoked = any(
        "web_search" in getattr(b, "type", "")
        or getattr(b, "type", "") == "server_tool_use"
        for b in resp.content
    )
    usage = {
        "input_tokens": getattr(resp.usage, "input_tokens", None),
        "output_tokens": getattr(resp.usage, "output_tokens", None),
    }
    return text, search_invoked, resp.model_dump(), usage


def call_openai(cell: dict):
    from openai import OpenAI

    client = OpenAI()  # reads OPENAI_API_KEY
    kwargs = dict(model=cell["model_id"], input=cell["prompt"])
    if cell["search"]:
        kwargs["tools"] = [{"type": "web_search"}]
    if cell["supports_temperature"]:
        kwargs["temperature"] = cell["temperature"]

    resp = client.responses.create(**kwargs)
    text = getattr(resp, "output_text", "") or ""
    raw = resp.model_dump()
    output_items = raw.get("output", []) or []
    search_invoked = any(
        isinstance(item, dict) and item.get("type") == "web_search_call"
        for item in output_items
    )
    usage = raw.get("usage", {}) or {}
    return text, search_invoked, raw, usage


def call_gemini(cell: dict):
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    tools = [types.Tool(google_search=types.GoogleSearch())] if cell["search"] else None
    gen_config = types.GenerateContentConfig(
        tools=tools,
        temperature=cell["temperature"] if cell["supports_temperature"] else None,
        max_output_tokens=cell["max_tokens"],
    )
    resp = client.models.generate_content(
        model=cell["model_id"],
        contents=cell["prompt"],
        config=gen_config,
    )
    text = resp.text or ""
    search_invoked = False
    try:
        cand = resp.candidates[0]
        gm = getattr(cand, "grounding_metadata", None)
        # grounding_metadata is populated only when search actually fired
        search_invoked = bool(
            gm and (getattr(gm, "grounding_chunks", None) or getattr(gm, "web_search_queries", None))
        )
    except (AttributeError, IndexError, TypeError):
        pass
    raw = resp.model_dump() if hasattr(resp, "model_dump") else {"text": text}
    usage = {}
    try:
        um = resp.usage_metadata
        usage = {
            "input_tokens": getattr(um, "prompt_token_count", None),
            "output_tokens": getattr(um, "candidates_token_count", None),
        }
    except AttributeError:
        pass
    return text, search_invoked, raw, usage


ADAPTERS = {
    "anthropic": call_anthropic,
    "openai": call_openai,
    "gemini": call_gemini,
}


# --------------------------------------------------------------------------
# Main loop
# --------------------------------------------------------------------------
def load_done_ids(out_path: Path) -> set[str]:
    done = set()
    if out_path.exists():
        with out_path.open() as f:
            for line in f:
                try:
                    rec = json.loads(line)
                    if rec.get("status") == "ok":
                        done.add(rec["call_id"])
                except json.JSONDecodeError:
                    continue
    return done


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", default="config.yaml")
    ap.add_argument("--prompts", default="prompts.yaml")
    ap.add_argument("--dry-run", action="store_true", help="print plan, call nothing")
    ap.add_argument("--limit", type=int, default=None, help="cap number of new cells")
    ap.add_argument("--sleep", type=float, default=0.5, help="seconds between calls")
    args = ap.parse_args()

    config = yaml.safe_load(Path(args.config).read_text())
    prompts = yaml.safe_load(Path(args.prompts).read_text())
    cells = build_cells(config, prompts)

    RESULTS_DIR.mkdir(exist_ok=True)
    today = dt.date.today().isoformat()
    out_path = RESULTS_DIR / f"run_{today}.jsonl"
    done = load_done_ids(out_path)

    pending = [c for c in cells if call_id(c) not in done]
    print(f"Total cells: {len(cells)} | already collected today: {len(done)} "
          f"| pending: {len(pending)}")

    if args.dry_run:
        from collections import Counter
        by_model = Counter(c["model_label"] for c in cells)
        by_type = Counter((c["query_type"], c["search"]) for c in cells)
        print("\nPer model:")
        for k, v in by_model.items():
            print(f"  {k}: {v}")
        print("\nPer (query_type, search):")
        for k, v in by_type.items():
            print(f"  {k}: {v}")
        return

    if args.limit:
        pending = pending[: args.limit]

    schema_version = config.get("schema_version", "1")
    n_ok = n_err = 0
    with out_path.open("a") as out:
        for i, cell in enumerate(pending, 1):
            cid = call_id(cell)
            rec = {
                "call_id": cid,
                "schema_version": schema_version,
                "timestamp_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
                "date": today,
                **{k: cell[k] for k in [
                    "provider", "model_id", "model_label", "tier",
                    "query_id", "query_type", "phrasing_idx", "prompt",
                    "search", "replicate", "temperature",
                ]},
            }
            adapter = ADAPTERS.get(cell["provider"])
            if adapter is None:
                rec.update(status="error", error=f"no adapter for {cell['provider']}")
                out.write(json.dumps(rec) + "\n"); out.flush()
                n_err += 1
                continue
            t0 = time.time()
            try:
                text, search_invoked, raw, usage = adapter(cell)
                rec.update(
                    status="ok",
                    response_text=text,
                    search_offered=cell["search"],
                    search_invoked=search_invoked,
                    latency_s=round(time.time() - t0, 3),
                    usage=usage,
                    raw=raw,
                )
                n_ok += 1
            except Exception as e:  # noqa: BLE001 — we want to log everything
                rec.update(
                    status="error",
                    error=f"{type(e).__name__}: {e}",
                    traceback=traceback.format_exc(),
                    latency_s=round(time.time() - t0, 3),
                )
                n_err += 1
            out.write(json.dumps(rec) + "\n"); out.flush()
            tag = "OK " if rec["status"] == "ok" else "ERR"
            si = "S+" if rec.get("search_invoked") else "s-"
            print(f"[{i}/{len(pending)}] {tag} {si} {cell['model_label']:<22} "
                  f"{cell['query_id']:<22} rep{cell['replicate']}")
            time.sleep(args.sleep)

    print(f"\nDone. ok={n_ok} err={n_err}. Wrote {out_path}")


if __name__ == "__main__":
    main()
