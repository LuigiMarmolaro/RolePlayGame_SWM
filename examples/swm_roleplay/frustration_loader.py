"""Few-shot pool of negotiator-frustration examples.

The agents' frustration / disengagement behaviour is NOT hardcoded in Python.
Instead, when the seriousness signal trips (player has been unserious or
off-topic), this module injects a small set of example exchanges into the
prompt. The model sees the *form* of natural negotiator frustration and
generates its own variant — different every time, in its own voice.

The pool is built from two sources:
  1. A small set of HAND-WRITTEN defaults at the bottom of this file (always
     available, ships with the game).
  2. Any ``*.jsonl`` file in ``training/frustration/`` (overrides + extends
     the defaults). Each line is one example:

        {"player": "...", "negotiator": "..."}

     or a multi-turn:

        {"turns": [{"by": "player", "text": "..."},
                   {"by": "negotiator", "text": "..."}, ...]}

Both formats are accepted. Strict rules apply to anything in this pool:

  - examples must be DOMAIN-AGNOSTIC (no City X facts, no specific places,
    organisations, projects, currencies or numbers — only the *form* of the
    response carries over);
  - examples should show the RANGE of natural reactions: mild push-back, curt
    refusal, frustration, calling out a contradiction, walking away.

The prompt block carries these rules explicitly so the model copies form, not
content.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import List, Optional

_HERE = Path(__file__).resolve().parent
_FRUSTRATION_CANDIDATES = [
    _HERE / "training" / "frustration",
    _HERE.parents[1] / "training" / "frustration",
]

# Cap so the prompt stays bounded on cheap/fast models (Flash-Lite).
MAX_EXAMPLES = 6
MAX_BLOCK_CHARS = 2400


def _frustration_dir() -> Optional[Path]:
    for c in _FRUSTRATION_CANDIDATES:
        if c.is_dir():
            return c
    return None


def _normalize_record(rec: dict) -> Optional[List[dict]]:
    """Accept either {player, negotiator} (single round-trip) or
    {turns: [{by, text}, ...]} (multi-turn). Return turns list."""
    if "turns" in rec and isinstance(rec["turns"], list):
        turns = [t for t in rec["turns"]
                 if isinstance(t, dict) and t.get("by") in ("player", "negotiator")
                 and isinstance(t.get("text"), str)]
        return turns if turns else None
    if "player" in rec and "negotiator" in rec:
        return [
            {"by": "player", "text": str(rec["player"])},
            {"by": "negotiator", "text": str(rec["negotiator"])},
        ]
    return None


def _load_jsonl_files() -> List[List[dict]]:
    root = _frustration_dir()
    if root is None:
        return []
    out: List[List[dict]] = []
    for path in sorted(root.glob("*.jsonl")):
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            t = _normalize_record(rec)
            if t:
                out.append(t)
    return out


# --- Hand-written defaults (always available, domain-agnostic). ---------
_DEFAULT_EXAMPLES: List[List[dict]] = [
    # Mild push-back
    [{"by": "player", "text": "let's just do whatever, I don't really care about the details"},
     {"by": "negotiator", "text": "Then we don't really have a negotiation. Bring me a proposal "
                                  "that names actors and amounts and I'll engage with it."}],
    # Curt
    [{"by": "player", "text": "just pick a number, any number works"},
     {"by": "negotiator", "text": "I'm not going to invent your position for you. I'm here to negotiate, "
                                  "not to write your homework."}],
    # Off-topic
    [{"by": "player", "text": "hey did you watch the game last night"},
     {"by": "negotiator", "text": "Happy to chat after the deadline. For now, name your conditions "
                                  "or I move to a vote."}],
    # Frustrated — walking away
    [{"by": "player", "text": "haha relax, it's just a game, lighten up"},
     {"by": "negotiator", "text": "This isn't a game for the people I represent. I'm stepping back "
                                  "from this dimension until there is a serious counter-offer."}],
    # Calling out a contradiction (multi-turn)
    [{"by": "player", "text": "I want it all to be free and immediate"},
     {"by": "negotiator", "text": "Two turns ago you said you would pay for monitoring. "
                                  "Decide which one is your real position, and I'll engage."}],
    # Refusing to engage on fantasy
    [{"by": "player", "text": "let's pretend money grows on trees and just commit"},
     {"by": "negotiator", "text": "If we negotiate from fantasy, my answer is no. Come back with "
                                  "a real funding source."}],
    # Sarcastic disengagement, vary the voice
    [{"by": "player", "text": "fine, whatever you say, you decide everything anyway"},
     {"by": "negotiator", "text": "I'm not going to negotiate against myself. When you have a "
                                  "position, I'll meet it."}],
    # Soft re-engagement after the player gets serious again
    [{"by": "player", "text": "ok, serious now: I propose a named fund of X with quarterly reporting"},
     {"by": "negotiator", "text": "That's a real proposal. Let me respond to it specifically — "
                                  "the fund size and the reporting cadence are workable, the "
                                  "named-source question is where we still need to land."}],
]


@lru_cache(maxsize=1)
def load_examples() -> List[List[dict]]:
    """Hand-written defaults first, then anything found in JSONL files."""
    pool: List[List[dict]] = list(_DEFAULT_EXAMPLES)
    pool.extend(_load_jsonl_files())
    return pool


def frustration_examples_block(max_examples: int = MAX_EXAMPLES) -> str:
    """A ready-to-inject prompt section with up to N example exchanges
    illustrating natural negotiator frustration / disengagement.

    Returns '' if the pool is empty (shouldn't happen — defaults are baked
    in)."""
    pool = load_examples()
    if not pool:
        return ""
    picks = pool[:max_examples]
    rendered: List[str] = []
    for ex in picks:
        lines: List[str] = []
        for t in ex:
            label = "PLAYER" if t["by"] == "player" else "NEGOTIATOR"
            lines.append(f"  {label}: {t['text']}")
        rendered.append("\n".join(lines))
    block = "\n\n".join(rendered)
    if len(block) > MAX_BLOCK_CHARS:
        block = block[:MAX_BLOCK_CHARS] + "\n  …"
    return (
        "FEW-SHOT — natural negotiator frustration / disengagement.\n"
        "Use these only to copy the *form* of authentic reactions to a\n"
        "non-serious counterpart. STRICT RULES:\n"
        "- DO NOT copy any sentence verbatim.\n"
        "- DO NOT mention any names, places, organisations, currencies, or\n"
        "  numbers from these examples — they are domain-agnostic samples.\n"
        "- Choose the response that fits THIS specific moment: it may be\n"
        "  mild, curt, frustrated, sarcastic, contradiction-calling, or a\n"
        "  full walk-away. Vary it; do not repeat what you said last turn.\n"
        "EXAMPLES:\n"
        f"{block}\n"
        "END OF FEW-SHOT. Now respond IN CHARACTER for your stakeholder.\n"
    )
