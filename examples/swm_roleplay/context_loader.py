"""Real-world background loader.

Reads every PDF / DOCX in the ``context/`` folder once at first call and
returns a single compiled excerpt string that gets injected into agent
prompts. The text is trimmed so prompts stay bounded for cheap/fast models.

Looks for the folder in two places (in order):
  1. ``examples/swm_roleplay/context/``  (next to streamlit_app.py)
  2. ``<repo root>/context/``            (where you actually put it)
"""
from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path
from typing import List

_HERE = Path(__file__).resolve().parent
_CANDIDATES = [_HERE / "context", _HERE.parents[1] / "context"]

# Budgets keep the prompt bounded so cheap models (Flash-Lite) stay fast.
MAX_PER_FILE_CHARS = 2800
MAX_TOTAL_CHARS = 8000


def _read_pdf(path: Path) -> str:
    try:
        from pypdf import PdfReader
        reader = PdfReader(str(path))
        return "\n".join((page.extract_text() or "") for page in reader.pages)
    except Exception:
        return ""


def _read_docx(path: Path) -> str:
    try:
        import docx
        d = docx.Document(str(path))
        return "\n".join(p.text for p in d.paragraphs)
    except Exception:
        return ""


def _clean(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def context_dir() -> Path | None:
    for c in _CANDIDATES:
        if c.is_dir():
            return c
    return None


@lru_cache(maxsize=1)
def reference_background() -> str:
    """One compiled excerpt string. Cached after first call.

    Returns '' if no context folder / no readable docs are found, so the rest
    of the app keeps working without context.
    """
    root = context_dir()
    if root is None:
        return ""
    pieces: List[str] = []
    total = 0
    seen: set[str] = set()
    for path in sorted(root.rglob("*")):
        name = path.name
        if name.startswith(".") or name in seen:
            continue
        ext = path.suffix.lower()
        if ext == ".pdf":
            text = _read_pdf(path)
        elif ext == ".docx":
            text = _read_docx(path)
        else:
            continue
        text = _clean(text)
        if not text:
            continue
        seen.add(name)
        excerpt = text[:MAX_PER_FILE_CHARS]
        pieces.append(f"[{name}]\n{excerpt}")
        total += len(excerpt)
        if total >= MAX_TOTAL_CHARS:
            break
    out = "\n\n".join(pieces)
    return out[:MAX_TOTAL_CHARS]


def reference_background_block() -> str:
    """The same excerpts wrapped as a ready-to-inject prompt section.

    Important framing: these documents are *training/knowledge material*, not
    part of the scenario. They make the agent sound like an informed
    solid-waste-management negotiator (vocabulary, typical mechanisms,
    realistic community/worker/government dynamics) — but the agent MUST
    NOT cite, quote, or reference the specific places, organizations,
    projects, or numbers in them. Only the City X scenario provides facts.
    """
    bg = reference_background()
    if not bg:
        return ""
    return (
        "BACKGROUND READING (NOT the scenario — use ONLY to inform your "
        "general expertise, vocabulary, sense of realistic mechanisms, "
        "and the typical concerns of stakeholders in solid-waste-management "
        "negotiations).\n"
        "STRICT RULES about this background:\n"
        "- DO NOT quote, cite or paraphrase these documents.\n"
        "- DO NOT mention any place name, organization, project name, "
        "country, currency or specific number from these documents.\n"
        "- The only places/people/numbers you may reference are those from "
        "the City X scenario itself or what the player has actually said.\n"
        "- Use this material only to sound like a knowledgeable negotiator "
        "who has read the relevant literature on this domain.\n"
        f"BACKGROUND TEXT:\n{bg}\n"
        "END OF BACKGROUND. Resume the City X negotiation; the rules above "
        "still apply.\n"
    )
