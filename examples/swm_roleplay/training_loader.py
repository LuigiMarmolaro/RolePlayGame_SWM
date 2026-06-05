"""Negotiation-skills loader.

Reads the CaSiNo dataset (annotated negotiation dialogues) once and exposes a
short prompt block that lists named negotiation *moves* with one real-human
example each. Agents read this to negotiate more skilfully — they do NOT
copy the wording or the example domain (campsite items). Strict rules in the
block enforce that.

Looks for the CaSiNo file in two locations:
  examples/swm_roleplay/training/CaSiNo-main/data/casino.json
  <repo root>/training/CaSiNo-main/data/casino.json
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Tuple

_HERE = Path(__file__).resolve().parent
_CASINO_CANDIDATES = [
    _HERE / "training" / "CaSiNo-main" / "data" / "casino.json",
    _HERE.parents[1] / "training" / "CaSiNo-main" / "data" / "casino.json",
]

# CaSiNo strategy taxonomy (Chawla et al. 2021, NAACL).
# Plain-English description per label so the model can use them in any domain.
STRATEGY_DESCRIPTIONS: Dict[str, str] = {
    "small-talk": "warm, brief social opening; show goodwill before negotiating",
    "showing-empathy": "acknowledge the other party's situation or constraints",
    "elicit-pref": "ask what the other side most cares about / where they can flex",
    "self-need": "give a concrete personal/role-based reason WHY you need something",
    "other-need": "argue that a third party (your constituents) needs it",
    "no-need": "concede an item or condition you don't actually need — signal a trade",
    "promote-coordination": "propose a joint plan or framing of mutual gain",
    "vouch-fair": "appeal to fairness, reciprocity, or balance of concessions",
    "uv-part": "(use sparingly) probe / challenge the other side's stated need",
}

# Order shown in the prompt — small-talk and self-need first because they are
# the most general moves; uv-part last because it is the most adversarial.
_ORDER = [
    "small-talk", "showing-empathy", "elicit-pref", "self-need",
    "other-need", "no-need", "promote-coordination", "vouch-fair", "uv-part",
]


def _find_casino_path() -> Path | None:
    for p in _CASINO_CANDIDATES:
        if p.is_file():
            return p
    return None


@lru_cache(maxsize=1)
def _examples_per_strategy() -> Dict[str, str]:
    """Pick one short, generic example utterance per strategy from CaSiNo.
    Filters out utterances mentioning the dataset's specific items so the
    examples illustrate *form* rather than content."""
    path = _find_casino_path()
    if path is None:
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    forbidden = ("firewood", "food package", "water package", "packages of food", "campsite")
    picks: Dict[str, str] = {}
    for dlg in data:
        ann = dlg.get("annotations") or []
        for utt, labels in ann:
            if not labels or not isinstance(utt, str):
                continue
            words = utt.split()
            if not (8 <= len(words) <= 26):
                continue
            lower = utt.lower()
            if any(f in lower for f in forbidden):
                continue
            for label in (lab.strip() for lab in labels.split(",")):
                if label in STRATEGY_DESCRIPTIONS and label not in picks:
                    picks[label] = utt.strip()
        if all(s in picks for s in STRATEGY_DESCRIPTIONS):
            break
    return picks


@lru_cache(maxsize=1)
def negotiation_skills_block() -> str:
    """Ready-to-inject prompt section. Empty string if CaSiNo isn't present."""
    examples = _examples_per_strategy()
    if not examples:
        return ""
    rows: List[str] = []
    for name in _ORDER:
        desc = STRATEGY_DESCRIPTIONS[name]
        ex = examples.get(name, "")
        if ex:
            rows.append(f"- {name}: {desc}\n    example form: \"{ex}\"")
        else:
            rows.append(f"- {name}: {desc}")
    table = "\n".join(rows)
    return (
        "NEGOTIATION SKILLS (drawn from a published annotated corpus of "
        "real human negotiations — CaSiNo, Chawla et al. 2021). Use these "
        "named moves to negotiate more skilfully, picking the right move "
        "for the moment. The example after each label shows *the form / "
        "style* of that move only.\n"
        "STRICT RULES about these examples:\n"
        "- DO NOT copy the example sentences.\n"
        "- DO NOT mention the example domain (camping, dogs, packages, "
        "diabetes etc.) — those are from another dataset, not City X.\n"
        "- Use only City X facts and the player's words for any concrete "
        "reference; the corpus is here purely to teach you the *moves*.\n"
        f"MOVES:\n{table}\n"
        "END OF NEGOTIATION SKILLS.\n"
    )


def available_strategies() -> Tuple[str, ...]:
    """Convenience accessor for tests / logs."""
    return tuple(STRATEGY_DESCRIPTIONS.keys())
