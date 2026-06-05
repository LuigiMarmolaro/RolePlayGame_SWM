"""Stakeholder relationship matrix.

Encodes — for every pair of City X stakeholders — what their relationship is,
which dimensions they NATURALLY negotiate about, and what they MUST NOT ask
each other (e.g., the National Government cannot ask the Community Leader for
money; it can only ask about needs and outcomes).

This matrix is injected into:
- the proposal-reaction prompt (so the AI speaking to the player respects the
  pair's allowed topics / forbidden asks);
- the role-reveal screen (so the human player sees their relationship with
  every other stakeholder up-front);
- the moderator's bilateral-suggestion prompt (so the moderator can suggest
  the two stakeholders most relevant to a given dimension).
"""
from __future__ import annotations

from typing import Dict, Iterable, List, Optional, Tuple


# Canonical role ids — mirrors streamlit_app.ROUND1_ORDER. Single source of
# truth here so the matrix below stays terse.
NAT, MUNI, PRIV, NGO, COM, INF = (
    "national_government",
    "municipal_government",
    "private_sector_company",
    "ngo_civil_society",
    "community_member",     # display_name has been renamed to "Community Leader"
    "informal_sector_worker",
)

# Dimension ids (mirrors NEGOTIABLE_DIMENSIONS + the two pre-set ones).
FIN, HEALTH, LIVE, MON = (
    "financing",
    "community_health_protections",
    "livelihoods",
    "monitoring_and_enforcement",
)
CORE, TIME = "core_action", "timeline"

# ---------------------------------------------------------------------------
# The matrix. Each (A, B) entry describes the relationship from A's side
# (most are symmetric, but power/asks are not). Topics = dimensions the pair
# can substantively negotiate. forbidden_asks = things A cannot demand of B.
#
# Keep this DENSE rather than DRY: explicit pairs are easier for a future
# editor / supervisor to skim.
# ---------------------------------------------------------------------------
_PairEntry = Dict[str, object]


def _pair(relation: str, power: str, topics: Iterable[str],
          forbidden_asks: Iterable[str]) -> _PairEntry:
    return {
        "relation": relation,
        "power": power,                   # "A_over_B" / "B_over_A" / "mutual" / "none"
        "topics": list(topics),
        "forbidden_asks": list(forbidden_asks),
    }


RELATIONS: Dict[Tuple[str, str], _PairEntry] = {
    # --- National Government ----------------------------------------------
    (NAT, MUNI): _pair(
        "hierarchical authority (national over local)",
        "A_over_B",
        [FIN, MON, TIME],
        ["unilateral unfunded mandates without compensating transfers"],
    ),
    (NAT, PRIV): _pair(
        "regulator / regulated investor",
        "mutual",
        [FIN, MON],
        ["below-market private capital with no public guarantee"],
    ),
    (NAT, NGO): _pair(
        "policy authority / civil-society advocate",
        "A_over_B",
        [MON, HEALTH, LIVE],
        ["financial contributions from the NGO",
         "the NGO to endorse measures it considers unsafe"],
    ),
    (NAT, COM): _pair(
        "state ↔ citizens (duty of care)",
        "A_over_B",
        [HEALTH, LIVE],
        ["any monetary contribution from residents",
         "technical or regulatory commitments residents cannot make"],
    ),
    (NAT, INF): _pair(
        "state ↔ informal workforce (legalisation / transition)",
        "A_over_B",
        [LIVE, MON],
        ["capital investment from informal workers",
         "performance guarantees workers cannot make"],
    ),

    # --- Municipal Government ---------------------------------------------
    (MUNI, PRIV): _pair(
        "contracting authority / operator",
        "mutual",
        [FIN, MON, HEALTH, TIME],
        ["the operator to absorb politically unfunded liabilities"],
    ),
    (MUNI, NGO): _pair(
        "monitored party / monitor",
        "B_over_A",
        [MON, HEALTH],
        ["financial contributions from the NGO"],
    ),
    (MUNI, COM): _pair(
        "service provider ↔ affected residents",
        "A_over_B",
        [HEALTH, LIVE, MON, TIME],
        ["money from residents",
         "compliance commitments residents cannot enforce themselves"],
    ),
    (MUNI, INF): _pair(
        "employer-of-record candidate ↔ informal workforce",
        "A_over_B",
        [LIVE, MON],
        ["unpaid labour beyond agreed transition tasks",
         "capital from workers"],
    ),

    # --- Private Sector ---------------------------------------------------
    (PRIV, NGO): _pair(
        "operator / watchdog",
        "B_over_A",
        [MON, HEALTH, LIVE],
        ["financial contributions from the NGO"],
    ),
    (PRIV, COM): _pair(
        "operator / host community",
        "mutual",
        [HEALTH, LIVE, MON],
        ["monetary contributions from residents",
         "residents to waive enforceable safeguards"],
    ),
    (PRIV, INF): _pair(
        "contracting party / informal workforce",
        "A_over_B",
        [LIVE, MON],
        ["capital investment from workers",
         "below-living-wage commitments"],
    ),

    # --- NGO / Civil Society ---------------------------------------------
    (NGO, COM): _pair(
        "advocacy ally (NGO speaks alongside the community)",
        "mutual",
        [HEALTH, LIVE, MON],
        ["money from residents"],
    ),
    (NGO, INF): _pair(
        "advocacy ally (NGO supports informal workers)",
        "mutual",
        [LIVE, MON],
        ["capital from workers"],
    ),

    # --- Community ↔ Informal Workers ------------------------------------
    (COM, INF): _pair(
        "solidarity ally (both bear elite-decision costs)",
        "mutual",
        [LIVE, HEALTH],
        ["money or capital from each other"],
    ),
}


def _normalize(a: str, b: str) -> Tuple[str, str]:
    """Return the matrix key. The matrix only stores (A, B); we look up both."""
    if (a, b) in RELATIONS:
        return (a, b)
    if (b, a) in RELATIONS:
        return (b, a)
    return (a, b)


def get(a: str, b: str) -> Optional[_PairEntry]:
    if a == b:
        return None
    key = _normalize(a, b)
    return RELATIONS.get(key)


def pair_brief(a: str, b: str) -> str:
    """One-line plain-English description for UI/role-reveal use."""
    rel = get(a, b)
    if not rel:
        return ""
    return rel["relation"]


def topics_for(a: str, b: str) -> List[str]:
    rel = get(a, b)
    return list(rel["topics"]) if rel else []


def forbidden_asks_from(a: str, b: str) -> List[str]:
    """What A cannot demand of B (orientation matters here)."""
    rel = get(a, b)
    if not rel:
        return []
    # Symmetric for now: the listed forbidden asks apply to both sides; we
    # could refine later by direction if needed.
    return list(rel["forbidden_asks"])


def relationship_block(speaker_role: str, listener_role: str,
                       dimension_id: Optional[str] = None) -> str:
    """A ready-to-inject prompt section describing this pair's relationship,
    allowed topics and forbidden asks. Used in the reaction prompt where the
    AI is ``speaker_role`` and the player (or another AI) is ``listener_role``.
    """
    rel = get(speaker_role, listener_role)
    if not rel:
        return ""
    topics = ", ".join(rel["topics"]) or "(no obvious shared dimension)"
    forbidden = "; ".join(rel["forbidden_asks"]) or "none specifically flagged"
    dim_note = ""
    if dimension_id and dimension_id not in rel["topics"]:
        dim_note = (
            f"\nNOTE: {dimension_id} is NOT a natural shared dimension for "
            "this pair. Stay specific about your own stake and either refer "
            "the question to a more relevant stakeholder or argue indirectly "
            "(values / framing) rather than making demands the other side "
            "cannot deliver.\n"
        )
    return (
        "STAKEHOLDER RELATIONSHIP CONTEXT (between you and the other speaker):\n"
        f"- Relationship: {rel['relation']}\n"
        f"- Power direction: {rel['power']}\n"
        f"- Natural shared topics: {topics}\n"
        f"- DO NOT demand or expect from this party: {forbidden}\n"
        f"{dim_note}"
        "Use this to keep your asks realistic — never request something the "
        "other party structurally cannot give.\n"
    )


def player_relationships_block(player_role: str,
                               display_names: Dict[str, str]) -> str:
    """For the role-reveal screen: a HTML <ul> of the player's relationship
    with every other stakeholder. ``display_names`` maps role_id → label."""
    rows: List[str] = []
    for other in (NAT, MUNI, PRIV, NGO, COM, INF):
        if other == player_role:
            continue
        rel = get(player_role, other)
        if not rel:
            continue
        topics = ", ".join(t for t in rel["topics"]) or "—"
        rows.append(
            f"<li><b>{display_names.get(other, other)}</b> — "
            f"{rel['relation']}. "
            f"<i>Shared topics:</i> {topics}.</li>"
        )
    if not rows:
        return ""
    return (
        "<div class='proposal-box'><b>Your relationships at the table</b>"
        "<ul style='margin:6px 0 0;padding-left:20px;'>"
        + "".join(rows)
        + "</ul></div>"
    )


# ---------------------------------------------------------------------------
# Per-role guidance on each dimension — frames the player's input correctly
# (e.g., National Gov on Finance MUST give a budget figure; Community Leader
# CANNOT, only needs/outcomes).
# ---------------------------------------------------------------------------
_ROLE_DIM_HINTS: Dict[Tuple[str, str], str] = {
    # National Government — owns Finance numbers and policy levers.
    (NAT, FIN): ("State a concrete first-year national budget figure with a "
                 "named source (treasury allocation, intergovernmental "
                 "transfer, etc.) and conditions for release."),
    (NAT, HEALTH): ("Frame this as regulatory standards and mandated transfers; "
                    "do not promise the operational delivery — that sits with "
                    "the municipality and the operator."),
    (NAT, LIVE): ("Frame this as policy levers (worker registration, training "
                  "funds, social protection) — the figures should come from "
                  "you; delivery is municipal."),
    (NAT, MON): ("Specify the named independent body, its legal basis and "
                 "reporting cadence — this is your authority to grant."),

    # Municipal Government — operational delivery, contracting, on-the-ground.
    (MUNI, FIN): ("Speak to municipal counterpart contributions, in-kind costs "
                  "and any tariff implications — leave the headline national "
                  "figure to the National Government."),
    (MUNI, HEALTH): ("Speak to operational measures the city actually runs "
                     "(clinics, leachate management, response timelines)."),
    (MUNI, LIVE): ("Speak to who you can absorb into the formal workforce, "
                   "training delivery and contract structures."),
    (MUNI, MON): ("Speak to inspections, public reporting and where civil "
                  "society's monitoring plugs into city operations."),

    # Private Sector — operator economics, investment, technical commitments.
    (PRIV, FIN): ("State capex/opex commitments and tariff implications; flag "
                  "the public guarantees you would need."),
    (PRIV, HEALTH): ("Commit to operational safety standards and harm-mitigation "
                     "investments at the site."),
    (PRIV, LIVE): ("Commit to workforce inclusion terms: who you will hire, "
                   "on what wages, with what training."),
    (PRIV, MON): ("Commit to data sharing, third-party verification and "
                  "penalty clauses."),

    # NGO / Civil Society — advocacy, monitoring, legitimacy. NEVER money.
    (NGO, FIN): ("Frame this around accountability and conditionality, NOT "
                 "around your financial contribution — you do not commit funds."),
    (NGO, HEALTH): ("State the protection thresholds you would consider "
                    "acceptable and the monitoring you would validate."),
    (NGO, LIVE): ("Speak for the workers and the community — what protections "
                  "and inclusion terms would you publicly endorse?"),
    (NGO, MON): ("Lead with named independent monitoring, public data, and a "
                 "community escalation pathway."),

    # Community Leader — needs, outcomes, lived experience. NEVER money/tech.
    (COM, FIN): ("Frame your input around needs and outcomes only — what "
                 "the funding has to achieve for households. You do NOT commit "
                 "money or technical mechanisms."),
    (COM, HEALTH): ("Speak from lived experience — health harms suffered, the "
                    "minimum protections households need from any deal."),
    (COM, LIVE): ("Speak to livelihood impacts on residents and what fair "
                  "treatment looks like for affected families."),
    (COM, MON): ("Speak to what would make oversight believable to residents — "
                 "who watches the watchers, how complaints are heard."),

    # Informal Sector Worker — livelihood survival, sector knowledge.
    (INF, FIN): ("Do NOT commit capital. Speak to the income protections, "
                 "transition support and sector inclusion your members need."),
    (INF, HEALTH): ("Speak to occupational health risks at the site and the "
                    "specific protections workers need."),
    (INF, LIVE): ("Be specific: registry, transition income, reserved roles, "
                  "training. This is your dimension to lead."),
    (INF, MON): ("Speak to worker representation in oversight bodies and "
                 "grievance mechanisms accessible to informal workers."),
}


def role_dimension_hint(role_id: str, dimension_id: str) -> str:
    return _ROLE_DIM_HINTS.get((role_id, dimension_id), "")


def most_relevant_pair_for(dimension_id: str) -> Optional[Tuple[str, str]]:
    """Return the pair (A, B) whose relationship most squarely covers a
    dimension — used by the moderator's bilateral-suggestion prompt."""
    # Hand-picked because these are the canonical "who should talk to whom"
    # mappings for City X:
    preferred = {
        FIN:    (NAT, MUNI),
        HEALTH: (COM, NGO),
        LIVE:   (INF, PRIV),
        MON:    (NGO, MUNI),
    }
    return preferred.get(dimension_id)
