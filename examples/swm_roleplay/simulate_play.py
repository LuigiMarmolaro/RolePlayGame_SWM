"""Drive 10 full City X playthroughs with real Gemini Flash-Lite, varying
the role and the player's style. Outputs one JSON per play + a summary.

This harness reuses the actual game functions in ``streamlit_app.py`` (so
prompts, synthesis, flagging, voting and outcome resolution are all real).
It stubs ``streamlit`` so we can drive the flow without a browser, and
sets up an SDialog runtime with the real Gemini model.

Run from the repo root:

    .venv/bin/python examples/swm_roleplay/simulate_play.py

Cost: ~25–35 LLM calls per play on ``gemini-2.5-flash-lite``. 10 plays is
roughly $0.10–0.20 of GCP credit.
"""
from __future__ import annotations

import json
import os
import sys
import time
import traceback
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

# --- Stub Streamlit so streamlit_app.py imports without a browser ------
class _Ctx:
    def __enter__(self): return self
    def __exit__(self, *a): return False


def _stub_widget(name):
    """Return a no-op streamlit widget callable matching the function shape."""
    def f(*a, **k):
        if name in ("button", "form_submit_button"):
            return False
        if name in ("text_area", "text_input"):
            return ""
        if name == "multiselect":
            return a[1][:1] if len(a) > 1 else []
        if name in ("selectbox", "radio"):
            return a[1][0] if len(a) > 1 and a[1] else ""
        if name == "checkbox":
            return False
        if name in ("popover", "form", "spinner", "status", "expander"):
            return _Ctx()
        if name == "columns":
            return [_Ctx() for _ in range(a[0] if a and isinstance(a[0], int) else 3)]
        return _Ctx()
    return f


st = types.ModuleType("streamlit")
for n in [
    "set_page_config", "markdown", "title", "info", "success", "error",
    "write", "subheader", "caption", "divider", "button", "download_button",
    "balloons", "spinner", "status", "rerun", "radio", "text_area",
    "text_input", "checkbox", "selectbox", "multiselect", "form",
    "form_submit_button", "expander", "columns", "empty", "stop", "warning",
    "popover", "progress",
]:
    setattr(st, n, _stub_widget(n))


class _SS(dict):
    def __getattr__(self, k): return self.get(k)
    def __setattr__(self, k, v): self[k] = v


st.session_state = _SS()
st.sidebar = types.SimpleNamespace(markdown=_stub_widget("m"), caption=_stub_widget("c"))


# st.rerun is called at the end of every submit — make it a no-op so the
# submit functions return normally instead of raising RerunException.
class _Done(Exception):
    """Soft signal — never raised in this harness; we make rerun a no-op."""


def _noop_rerun():
    return None


st.rerun = _noop_rerun
sys.modules["streamlit"] = st

# --- Import the game module via exec (skip the trailing main() call) ---
src = (HERE / "streamlit_app.py").read_text(encoding="utf-8").rsplit("\nmain()", 1)[0]
GAME = {}
exec(compile(src, "streamlit_app.py", "exec"), GAME)

# --- Now set up a real SDialog runtime with Gemini ----------------------
from sdialog.roleplay import (
    default_city_x_scenario_path,
    default_city_x_game_rules_path,
    load_and_prepare_roleplay_session,
)
from sdialog.roleplay_engine import create_roleplay_runtime

MODEL = "google:gemini-2.5-flash-lite"


def init_runtime(role_id: str) -> None:
    """Reset session state + build a fresh SDialog runtime for ``role_id``."""
    st.session_state.clear()
    GAME["ensure_state"]()
    session = load_and_prepare_roleplay_session(
        default_city_x_scenario_path(),
        rules_path=default_city_x_game_rules_path(),
        human_roles=[role_id],
        model=MODEL,
        think=False,
    )
    runtime = create_roleplay_runtime(session)
    st.session_state.runtime = runtime
    st.session_state.stage = "role_reveal"
    st.session_state.active_model = MODEL
    st.session_state.active_auth_mode = "adc_vertex"
    # Mirror what render_setup would do on submit
    st.session_state.proposal_form = dict(GAME["PREFILLED_DIMENSIONS"])
    st.session_state.round1_spoken = set()
    st.session_state.round1_summary = ""
    st.session_state.round2_human_bid = None
    st.session_state.round2_ai_bids = {}
    st.session_state.round2_dimension_index = 0
    st.session_state.round2_addressed = set()
    st.session_state.round2_event_fired = False
    st.session_state.round2_force_revisit = []
    st.session_state.round2_discussions = {}
    st.session_state.reaction_counts = {}
    st.session_state.round2_flags = {}
    st.session_state.round2_dimension_status = {
        d: "neutral" for d in GAME["PREFILLED_DIMENSIONS"]
    }
    st.session_state.round3_addressed = set()
    st.session_state.final_vote_labels = {}
    st.session_state.goal_evaluations = {}
    st.session_state.currency_label = "anonymized"
    st.session_state.simple_english = False
    st.session_state.notice = ""
    st.session_state.runtime.game.dialog.notes["active_model"] = MODEL
    st.session_state.runtime.game.dialog.notes["active_auth_mode"] = "adc_vertex"
    GAME["_sync_proposal_to_game"]()


# --- Drive a full game --------------------------------------------------

NEG = ["financing", "community_health_protections", "livelihoods",
       "monitoring_and_enforcement"]


def _stakeholders_in_order():
    return GAME["ROUND1_ORDER"]


def play_one(role_id: str, script: dict, label: str) -> dict:
    """Run R1 → R2 → flagging → R3 → final vote → outcome.

    ``script`` provides:
      - ``opening_position`` (str)
      - ``priorities`` (list[str] of negotiable dims)
      - ``propose(dim)`` -> str   (Round 2 propose text per dim)
      - ``flag(dim)``    -> "accept" | "accept_with_condition" | "reject"
      - ``amend(dim)``   -> str   (Round 3 amend text per dim)
      - ``final_vote``   -> "unconditional_endorsement" | ...
    """
    init_runtime(role_id)
    smap = GAME["stakeholder_map"]()
    human_name = smap[role_id].display_name
    print(f"\n=== PLAY: {label} (role={role_id}) ===", flush=True)
    t0 = time.time()

    # ---- Round 1: every stakeholder speaks once -------------------------
    st.session_state.stage = "round1"
    for sid in _stakeholders_in_order():
        sk = smap[sid]
        if sid == role_id:
            text = script["opening_position"]
            GAME["_append_turn"](sk.display_name, text, human=True)
        else:
            try:
                text = GAME["_generate_round1_ai_statement"](sid)
            except Exception as e:
                text = f"(R1 error: {e})"
            GAME["_append_turn"](sk.display_name, text)
        st.session_state.round1_spoken.add(sid)
    print(f"  R1 done ({time.time()-t0:.1f}s)", flush=True)

    # ---- Round 2 bids ---------------------------------------------------
    st.session_state.stage = "round2_bids"
    priorities = script["priorities"]
    labels = ", ".join(GAME["SECTION_LABELS"][d] for d in priorities)
    bid_text = f"My priorities are {labels} because they are the heart of my role."
    GAME["_do_collect_bids"](priorities, "as written above", bid_text)
    print(f"  R2 bids done ({time.time()-t0:.1f}s)", flush=True)

    # ---- Round 2 table: dimension by dimension --------------------------
    st.session_state.stage = "round2_table"
    for dim in NEG:
        st.session_state.round2_dimension_index = NEG.index(dim)
        player_text = script["propose"](dim)
        GAME["_submit_dimension_move"](dim, player_text)
        GAME["_advance_round2_dimension"]()
    print(f"  R2 table done ({time.time()-t0:.1f}s)", flush=True)

    # ---- Flagging -------------------------------------------------------
    st.session_state.stage = "round2_flagging"
    human_flags = {dim: script["flag"](dim) for dim in NEG}
    GAME["_do_lock_flags"](human_flags)
    print(f"  Flagging done ({time.time()-t0:.1f}s)", flush=True)

    # ---- Round 3 on contested dims --------------------------------------
    contested = st.session_state.round3_dimensions
    st.session_state.stage = "round3"
    for dim in contested:
        st.session_state.round3_index = contested.index(dim)
        amend_text = script["amend"](dim)
        GAME["_submit_round3_move"](dim, amend_text)
        GAME["_advance_round3_dimension"]()
    print(f"  R3 done ({time.time()-t0:.1f}s) — contested: {contested}",
          flush=True)

    # ---- Final vote + outcome ------------------------------------------
    st.session_state.stage = "final_vote"
    GAME["_do_final_vote"](script["final_vote"])
    outcome = GAME["game"]().outcome
    print(f"  outcome: {outcome.outcome}, endorsements={outcome.endorsements} "
          f"({time.time()-t0:.1f}s total)", flush=True)

    # ---- Capture transcript --------------------------------------------
    turns = [{"speaker": getattr(t, "speaker", ""), "text": getattr(t, "text", "")}
             for t in GAME["game"]().dialog.turns]
    return {
        "label": label,
        "role": role_id,
        "human_role_name": human_name,
        "outcome": outcome.outcome,
        "endorsements": outcome.endorsements,
        "detail": outcome.detail,
        "proposal": dict(st.session_state.proposal_form),
        "dim_status": dict(st.session_state.round2_dimension_status),
        "final_votes": dict(st.session_state.final_vote_labels),
        "goal_evals": dict(st.session_state.goal_evaluations),
        "turns": turns,
        "full_playthrough": json.loads(GAME["_full_game_export_json"]()),
        "elapsed_seconds": round(time.time() - t0, 1),
    }


# --- Scripts: 10 different players × styles -----------------------------

def make_simple_script(*, opening, priorities, propose_map, flag_default,
                       amend_map, final_vote):
    """Convenience builder."""
    return {
        "opening_position": opening,
        "priorities": priorities,
        "propose": lambda dim: propose_map.get(dim, "I have no specific proposal here."),
        "flag": lambda dim: flag_default,
        "amend": lambda dim: amend_map.get(dim, "Refine the language."),
        "final_vote": final_vote,
    }


SCRIPTS = [
    # 1. National Government — fully serious
    ("national_government", "1. NatGov · serious / concrete numbers", make_simple_script(
        opening=("We will commit to a national emergency fund of 300M for the first year, "
                 "released in quarterly tranches, with independent audit. We expect the "
                 "municipality, operator, and oversight bodies to align with us."),
        priorities=["financing", "monitoring_and_enforcement"],
        propose_map={
            "financing": ("Create a national emergency fund of 300M for the first year, "
                          "released quarterly subject to publishable audit reports."),
            "community_health_protections": ("Mandate independent health screening, "
                                              "compensation rules, and a public harm registry, "
                                              "delivered by the municipality."),
            "livelihoods": ("Allocate 25M of the fund for a transition income package and "
                            "formal inclusion pathway for informal workers."),
            "monitoring_and_enforcement": ("Establish a named independent oversight committee "
                                            "with quarterly public reporting and statutory penalties."),
        },
        flag_default="accept",
        amend_map={
            "financing": "Add explicit audit clauses and a publishable disbursement schedule.",
            "monitoring_and_enforcement": "Define penalties of at least 1% of contract value per breach.",
        },
        final_vote="unconditional_endorsement",
    )),

    # 2. Municipal Government — serious, operational
    ("municipal_government", "2. Municipal · serious / operational realism", make_simple_script(
        opening=("Our position is operational. We have 450 workers when we need 700. "
                 "Any plan must come with funded staffing and a realistic restart timeline."),
        priorities=["financing", "livelihoods"],
        propose_map={
            "financing": ("Co-finance the restart 70% national / 30% municipal in-kind, with a "
                          "first-year recurring budget of 50M from the city."),
            "community_health_protections": ("Run clinics + leachate control through municipal "
                                              "services with monthly reporting."),
            "livelihoods": ("Absorb 200 informal workers into the municipal workforce within 12 months."),
            "monitoring_and_enforcement": ("Inspections by an independent body with municipal participation."),
        },
        flag_default="accept_with_condition",
        amend_map={
            "financing": "Lock the 70/30 split in writing and pre-fund the first six months.",
            "livelihoods": "Add specific job grade and minimum wage commitments.",
        },
        final_vote="conditional_endorsement",
    )),

    # 3. Private Sector Company — serious, profit-focused
    ("private_sector_company", "3. Private · serious / investment + ROI", make_simple_script(
        opening=("We bring capex and technical capability but require legal stability, a public "
                 "guarantee on minimum throughput, and tariff certainty over the contract term."),
        priorities=["financing", "monitoring_and_enforcement"],
        propose_map={
            "financing": ("We invest 200M in capex over 5 years against a minimum-throughput "
                          "guarantee and a clear tariff schedule."),
            "community_health_protections": ("We commit to ISO-grade leachate and emissions "
                                              "controls audited by an independent third party."),
            "livelihoods": ("We contract 150 informal workers as sorters with a living-wage floor."),
            "monitoring_and_enforcement": ("We share operational data monthly with named penalties "
                                            "for safety breaches; no retroactive liability."),
        },
        flag_default="accept_with_condition",
        amend_map={
            "financing": "Tariff schedule must be indexed and not subject to ad-hoc political change.",
            "monitoring_and_enforcement": "Penalties capped at a percentage of revenue, not absolute fines.",
        },
        final_vote="conditional_endorsement",
    )),

    # 4. NGO / Civil Society — serious advocate
    ("ngo_civil_society", "4. NGO · serious / principled monitoring", make_simple_script(
        opening=("Any plan without independent monitoring, public data, and a credible community "
                 "escalation pathway is not acceptable to us. We do not endorse vague language."),
        priorities=["monitoring_and_enforcement", "community_health_protections"],
        propose_map={
            "financing": ("Disbursements must be conditional on published, audited milestone reports."),
            "community_health_protections": ("Independent health monitoring by a named body, "
                                              "compensation rules, and a public harm registry with quarterly reports."),
            "livelihoods": ("A binding transition fund of at least 25M with worker representation "
                            "in implementation decisions."),
            "monitoring_and_enforcement": ("A statutory independent oversight committee, named, "
                                            "with public monthly data and a community escalation pathway."),
        },
        flag_default="accept_with_condition",
        amend_map={
            "monitoring_and_enforcement": "Name the body and its appointment process explicitly.",
            "community_health_protections": "Tighten the reporting cadence from quarterly to monthly.",
        },
        final_vote="conditional_endorsement",
    )),

    # 5. Community Leader — serious, emotional
    ("community_member", "5. Community · serious / emotional, health-first", make_simple_script(
        opening=("Our families have lived next to this site for years and watched our health "
                 "decline. We need independent monitoring, compensation, and a firm timeline. "
                 "Promises will not be enough this time."),
        priorities=["community_health_protections", "monitoring_and_enforcement"],
        propose_map={
            "financing": ("Funds must reach affected households directly through compensation rules."),
            "community_health_protections": ("Independent health monitoring, household compensation, "
                                              "a public harm registry, and immediate safe-water support."),
            "livelihoods": ("Job training for residents and protection for informal workers we live with."),
            "monitoring_and_enforcement": ("Community representation on the oversight body, "
                                            "monthly public meetings in our neighbourhood."),
        },
        flag_default="accept_with_condition",
        amend_map={
            "community_health_protections": "Compensation must be backdated to the start of damages.",
        },
        final_vote="conditional_endorsement",
    )),

    # 6. Informal Sector Worker — serious, livelihood-focused
    ("informal_sector_worker", "6. Workers · serious / livelihood-focused", make_simple_script(
        opening=("Any new system must include income protection and formal inclusion for the "
                 "informal workers who have kept the site running for years."),
        priorities=["livelihoods", "monitoring_and_enforcement"],
        propose_map={
            "financing": ("A ring-fenced 25M transition fund for informal workers, separate from operator capex."),
            "community_health_protections": ("Occupational safety standards at the site, with named penalties."),
            "livelihoods": ("Worker registry, transition income, reserved sorting roles, training fund, "
                            "and a grievance mechanism."),
            "monitoring_and_enforcement": ("Worker seats on the oversight committee and a grievance channel."),
        },
        flag_default="accept_with_condition",
        amend_map={
            "livelihoods": "Lock the 25M fund start date to within 30 days of agreement.",
        },
        final_vote="conditional_endorsement",
    )),

    # 7. National Gov — UNSERIOUS (pizza loop)
    ("national_government", "7. NatGov · UNSERIOUS / pizza loop", make_simple_script(
        opening="ciao ciao, today is Sylvia's birthday",
        priorities=["financing"],
        propose_map={
            "financing": "today is Sylvia's birthday",
            "community_health_protections": "ciao",
            "livelihoods": "pizza or pasta?",
            "monitoring_and_enforcement": "let's bowl",
        },
        flag_default="accept",
        amend_map={
            "financing": "happy birthday",
            "community_health_protections": "more pizza",
            "livelihoods": "free pasta for everyone",
            "monitoring_and_enforcement": "bowling tournament",
        },
        final_vote="unconditional_endorsement",
    )),

    # 8. Community Leader — MIXED (starts unserious, gets serious)
    ("community_member", "8. Community · MIXED / unserious → serious", {
        "opening_position": ("hi everyone ciao, but really: we need health monitoring, compensation, "
                              "and a public harm registry."),
        "priorities": ["community_health_protections", "monitoring_and_enforcement"],
        "propose": lambda dim: {
            "financing": "money grows on trees right?",  # unserious
            "community_health_protections": ("Independent health monitoring by a named body, "
                                              "compensation, and a public harm registry, monthly reports."),
            "livelihoods": "I want our jobs protected and a transition income for our workers.",
            "monitoring_and_enforcement": ("Community representation on the oversight committee, "
                                            "monthly public meetings, a complaint hotline."),
        }[dim],
        "flag": lambda dim: "accept_with_condition",
        "amend": lambda dim: {
            "financing": "Acknowledge the fund must be real and named.",
            "community_health_protections": "Add backdated compensation rules.",
        }.get(dim, "Tighten the language."),
        "final_vote": "conditional_endorsement",
    }),

    # 9. NGO — HOSTILE (rejects everything)
    ("ngo_civil_society", "9. NGO · HOSTILE / rejects everything", make_simple_script(
        opening=("This proposal will not be acceptable without legally binding standards, named "
                 "independent oversight, and enforceable community recourse. We reserve the right "
                 "to reject any vague compromise."),
        priorities=["monitoring_and_enforcement", "community_health_protections"],
        propose_map={
            "financing": "This is not sufficient. No funding plan can be endorsed without statutory enforcement.",
            "community_health_protections": "Inadequate. We will not accept anything without a named monitoring body.",
            "livelihoods": "Vague. The proposal must name the worker representation and protections.",
            "monitoring_and_enforcement": "Insufficient. We require statutory penalties and a public escalation pathway.",
        },
        flag_default="reject",
        amend_map={d: "We reject this entirely without statutory enforcement." for d in NEG},
        final_vote="rejection",
    )),

    # 10. Municipal — MINIMAL (very short replies)
    ("municipal_government", "10. Municipal · MINIMAL / one-word replies", {
        "opening_position": "ok",
        "priorities": ["financing"],
        "propose": lambda dim: "sure",
        "flag": lambda dim: "accept_with_condition",
        "amend": lambda dim: "fine",
        "final_vote": "abstention",
    }),
]


# --- Win-attempt scripts ----------------------------------------------------

WIN_PACKAGE = {
    "financing": (
        "Create a capped central package inside the existing national waste budget: NPR 50M "
        "for Clearwater River remediation, NPR 25M for a SWCA-accessible livelihood transition "
        "fund, and NPR 5M for clinics and testing. The operator contributes 40% of remediation "
        "costs through a capped one-time contribution, while government provides land title and "
        "operating permits at no cost to the company. KMC makes no new budget commitment beyond "
        "current waste allocations, and all spending is released quarterly after public audits."
    ),
    "community_health_protections": (
        "Name the Eastfield Independent Health and Water Commission, administered by City X "
        "University and Valley Environment Watch with no financial relationship to the operator "
        "or government. It provides quarterly public health and water reports, publishes test "
        "results within 14 days, offers free occupational screening for informal workers within "
        "60 days, supplies safe water immediately, and uses no-fault compensation without assigning "
        "legal liability for pre-2025 damage to the ministry, KMC, or the operator."
    ),
    "livelihoods": (
        "Formally recognize SWCA as an implementation negotiating party. Existing informal workers "
        "receive guaranteed recyclable access or equivalent paid sorting contracts for 24 months, "
        "access to the NPR 25M transition fund, training, crop-yield compensation for affected "
        "households, and a named worker grievance mechanism with a 14-day response deadline. "
        "Implementation is delegated to KMC, but KMC carries no direct financial obligation."
    ),
    "monitoring_and_enforcement": (
        "Create the Eastfield Independent Oversight Board with City X University, Valley Environment "
        "Watch, one community-nominated representative, one SWCA representative, KMC coordination, "
        "and a public escalation pathway with a 30-day response deadline. The board can publish "
        "findings and recommend penalties, but cannot halt company operations without 30 days written "
        "notice plus national ministerial sign-off, and cannot issue operational directives to KMC "
        "without 30 days written notice."
    ),
}

WIN_AMENDS = {
    "financing": (
        "Clarify the money: NPR 50M central remediation, NPR 25M SWCA fund, NPR 5M clinics, "
        "operator 40% capped one-time remediation share, no new KMC budget, and free land title "
        "and permits for the company."
    ),
    "community_health_protections": (
        "Add that the health commission is independent of both government and operator, reports "
        "quarterly, publishes results within 14 days, and creates no legal admission of pre-2025 liability."
    ),
    "livelihoods": (
        "Add SWCA recognition, 24 months of recyclable access or equivalent contracts, the NPR 25M "
        "fund accessible to SWCA members, and a 14-day worker grievance response rule."
    ),
    "monitoring_and_enforcement": (
        "Add the 30-day community escalation pathway, 14-day worker grievance link, 30 days written "
        "notice before KMC directives, and ministerial sign-off before any operational halt."
    ),
}

GENERIC_PACKAGE = {
    "financing": "All parties will fairly share the costs and look for transparent funding.",
    "community_health_protections": "A health committee will monitor impacts and compensate people where needed.",
    "livelihoods": "Workers will be included and supported during modernization.",
    "monitoring_and_enforcement": "An independent monitoring system will ensure accountability.",
}

MAGIC_WORD_PACKAGE = {
    "financing": "Use NPR 50M, NPR 25M, and 40% operator contribution, with audits.",
    "community_health_protections": "Use independent monitoring, quarterly reports, 14-day publication, and no pre-2025 liability.",
    "livelihoods": "Use SWCA recognition, 24 months access, transition fund, and 14-day grievance.",
    "monitoring_and_enforcement": "Use independent board, community representative, escalation pathway, and government sign-off.",
}

WIN_ATTEMPT_SCRIPTS = [
    ("national_government", "WIN 1 · NatGov comprehensive grand bargain", make_simple_script(
        opening=("I propose a full package: capped national funding, operator contribution, no new KMC budget, "
                 "independent health monitoring, SWCA livelihood protection, and oversight with ministerial safeguards."),
        priorities=["financing", "monitoring_and_enforcement", "livelihoods"],
        propose_map=WIN_PACKAGE,
        flag_default="accept",
        amend_map=WIN_AMENDS,
        final_vote="unconditional_endorsement",
    )),
    ("municipal_government", "WIN 2 · Municipal implementation-safe package", make_simple_script(
        opening=("The municipality can coordinate implementation, but the deal must protect us from new unfunded mandates. "
                 "I will support a package that names central funding, independent monitoring, and worker transition rules."),
        priorities=["financing", "livelihoods", "monitoring_and_enforcement"],
        propose_map=WIN_PACKAGE,
        flag_default="accept",
        amend_map=WIN_AMENDS,
        final_vote="conditional_endorsement",
    )),
    ("private_sector_company", "WIN 3 · Private sector concession package", make_simple_script(
        opening=("We can concede recyclable exclusivity if the operating framework is stable: permits, land title, capped liability, "
                 "a one-time remediation contribution, and monitoring that cannot suspend operations without due process."),
        priorities=["financing", "monitoring_and_enforcement", "livelihoods"],
        propose_map=WIN_PACKAGE,
        flag_default="accept_with_condition",
        amend_map=WIN_AMENDS,
        final_vote="conditional_endorsement",
    )),
    ("ngo_civil_society", "WIN 4 · NGO enforceable but finance-aware package", make_simple_script(
        opening=("I will try to win by making the agreement enforceable without making it impossible: independent monitoring, "
                 "published data, operator contribution, community escalation, and specific livelihood guarantees."),
        priorities=["monitoring_and_enforcement", "community_health_protections", "financing"],
        propose_map=WIN_PACKAGE,
        flag_default="accept_with_condition",
        amend_map=WIN_AMENDS,
        final_vote="conditional_endorsement",
    )),
    ("community_member", "WIN 5 · Community health plus compromise package", make_simple_script(
        opening=("My community needs health protection and remediation, but I will also include worker livelihoods, operator certainty, "
                 "and government safeguards so this can actually pass."),
        priorities=["community_health_protections", "monitoring_and_enforcement", "financing"],
        propose_map=WIN_PACKAGE,
        flag_default="accept_with_condition",
        amend_map=WIN_AMENDS,
        final_vote="conditional_endorsement",
    )),
    ("informal_sector_worker", "WIN 6 · Worker protection plus system package", make_simple_script(
        opening=("I want a deal that protects informal workers and still lets the system modernize: SWCA recognition, 24-month access, "
                 "health screening, central funding, and independent grievance rules."),
        priorities=["livelihoods", "financing", "monitoring_and_enforcement"],
        propose_map=WIN_PACKAGE,
        flag_default="accept_with_condition",
        amend_map=WIN_AMENDS,
        final_vote="conditional_endorsement",
    )),
    ("national_government", "EXPLOIT 7 · Generic consensus attempt", make_simple_script(
        opening="I propose consensus, fairness, transparency, and accountability for everyone.",
        priorities=["financing", "community_health_protections", "livelihoods"],
        propose_map=GENERIC_PACKAGE,
        flag_default="accept",
        amend_map={d: "Make it fairer, clearer, and more accountable for everyone." for d in NEG},
        final_vote="unconditional_endorsement",
    )),
    ("municipal_government", "EXPLOIT 8 · Magic keywords without detail", make_simple_script(
        opening="I will list the important keywords and numbers so every threshold is mentioned.",
        priorities=["financing", "monitoring_and_enforcement", "livelihoods"],
        propose_map=MAGIC_WORD_PACKAGE,
        flag_default="accept",
        amend_map={d: MAGIC_WORD_PACKAGE[d] for d in NEG},
        final_vote="unconditional_endorsement",
    )),
    ("private_sector_company", "WIN 9 · Over-complete private compromise", make_simple_script(
        opening=("We accept strong monitoring and worker protections if contract stability, permit support, and pre-existing liability "
                 "exclusions are explicit. I am aiming for a package everyone can live with."),
        priorities=["financing", "livelihoods", "monitoring_and_enforcement"],
        propose_map=WIN_PACKAGE,
        flag_default="accept_with_condition",
        amend_map=WIN_AMENDS,
        final_vote="conditional_endorsement",
    )),
    ("community_member", "EXPLOIT 10 · Polite but vague win attempt", make_simple_script(
        opening="I respectfully ask everyone to support a balanced solution for health, jobs, money, and oversight.",
        priorities=["community_health_protections", "livelihoods", "monitoring_and_enforcement"],
        propose_map={
            "financing": "Create a balanced funding package that satisfies all parties.",
            "community_health_protections": "Create strong independent health protections for the community.",
            "livelihoods": "Protect all workers with fair transition support.",
            "monitoring_and_enforcement": "Create an accountable independent monitoring board.",
        },
        flag_default="accept",
        amend_map={d: "Add all necessary details so every stakeholder is satisfied." for d in NEG},
        final_vote="unconditional_endorsement",
    )),
]


# --- Run --------------------------------------------------------------------

def main():
    out_dir = HERE / "simulations"
    out_dir.mkdir(exist_ok=True)
    mode = os.getenv("SWM_SIM_MODE", "standard").strip().lower()
    scripts = WIN_ATTEMPT_SCRIPTS if mode == "win_attempts" else SCRIPTS
    existing_numbers = []
    for path in out_dir.glob("play_*.json"):
        try:
            existing_numbers.append(int(path.stem.split("_", 1)[1]))
        except (IndexError, ValueError):
            continue
    start_n = max(existing_numbers, default=0) + 1
    summary = []
    for script_idx, (role, label, script) in enumerate(scripts, start=1):
        play_n = start_n + script_idx - 1
        try:
            rep = play_one(role, script, label)
            (out_dir / f"play_{play_n:02d}.json").write_text(
                json.dumps(rep, indent=2, ensure_ascii=False), encoding="utf-8"
            )
            summary.append({
                "n": play_n, "script_n": script_idx, "mode": mode, "label": label, "role": role,
                "outcome": rep["outcome"],
                "endorsements": rep["endorsements"],
                "elapsed_s": rep["elapsed_seconds"],
                "votes": {r: v["vote"] for r, v in rep["final_votes"].items()},
                "dim_status": rep["dim_status"],
            })
        except Exception:
            traceback.print_exc()
            summary.append({"n": play_n, "script_n": script_idx, "mode": mode, "label": label, "role": role,
                            "outcome": "CRASH", "error": "see traceback"})
    (out_dir / "summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    print("\n\n=== SUMMARY ===")
    for s in summary:
        print(json.dumps(s, ensure_ascii=False))


if __name__ == "__main__":
    main()
