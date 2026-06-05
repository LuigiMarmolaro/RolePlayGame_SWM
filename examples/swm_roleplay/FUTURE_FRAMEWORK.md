# Future Framework — City X Negotiation Game

This document is the **theoretical scaffold** for the larger features from
the supervisor's spec that are **not implemented yet**. For each one, it
describes:

- the *intent* (what the player should experience),
- the *data model* (what new state/JSON fields are needed),
- the *prompt design* (how the LLM is asked),
- the *integration points* in the existing codebase,
- and the *risks / open questions* to settle before coding.

The goal is that a developer (or a future Claude Code session) can pick any
section below and start implementing without rediscovering the design.

---

## A. Background AI ↔ AI conversations

**Intent.** Stakeholders should talk to *each other* between rounds — not just
to the player. The player sees a *one-line summary* in the draft proposal
("Based on the following conversations: National Government spoke with NGO"),
not the full transcript.

### Data model

Extend `st.session_state` with:

```python
"bilateral_logs": [
    {
        "round": int,                 # 1, 2 or 3
        "dimension": str,              # e.g. "monitoring_and_enforcement"
        "a": str,                      # role_id
        "b": str,                      # role_id
        "summary": str,                # 1-sentence outcome
        "agreed_points": [str, ...],   # pulled into draft proposal
    },
]
```

### Prompt design

A new `_bilateral_prompt(a, b, dimension, context)` that produces a *2–4 turn*
synthetic exchange between two stakeholder agents on a single dimension.
Use SDialog's standard `Agent.dialog_with(Agent)` pattern (sdialog already
supports two agents talking — `examples/swm_roleplay/streamlit_app.py` only
uses stateless single-call mode today). Then ask the moderator agent to
condense the exchange to one sentence + a list of concrete agreed points.

### Integration points

- New module `bilaterals.py` next to `relationships.py`:
  - `run_bilateral(runtime, a, b, dim) -> dict` — runs the off-stage chat.
  - `summarize_bilateral(runtime, exchange) -> dict`.
- In `_advance_round2_dimension` and `_advance_round3_dimension`, *before*
  moving to the next dimension, fire one bilateral between the two parties
  named by `relationships.most_relevant_pair_for(dim)` (skip if either is
  the human player).
- In `_synthesize_dimension_proposal`, prepend any `agreed_points` from
  bilaterals on this dimension so they survive into the final text.

### Risks

- **Cost** — multiplies LLM calls per round by 4 (one bilateral per
  negotiable dimension). On Flash-Lite still cheap; on Pro not.
- **Latency** — sequential bilaterals could add 10–20 s to the "move to next
  dimension" step. Mitigate with `concurrent.futures` calling the LLM in
  parallel since each bilateral is independent.
- **Quality** — without good prompting, synthetic AI↔AI dialogues drift.
  Cap to 3 turns and feed the relationship matrix + dimension hint.

---

## B. Player-directed conversation mechanic

**Intent.** The player tells one stakeholder *"go talk to X about Y"*; the
draft proposal updates with the outcome of that conversation.

### UI sketch

On the Round 2 negotiation table, add a small panel:

```
🗣 Send another stakeholder to talk
   Send: [select stakeholder] → To: [select stakeholder]
   About: [dimension dropdown]
   [Trigger conversation]
```

### Data model

Reuse `bilateral_logs` from section A. Add a `triggered_by: "player" | "auto"`
field. The player's triggers should appear ranked first in the draft proposal
summary.

### Prompt design

Same as A's `run_bilateral`, plus an extra instruction:
*"The Community Leader (the player) explicitly asked you to discuss this —
they want a concrete outcome, not posturing."*

### Integration points

- Reuse `bilaterals.py`.
- In `render_round2_table`, render the UI panel between the moderator
  suggestion and the propose form.
- Block sending the player themselves as A or B (they're at the table, not
  off-stage).

### Risks

- Cost (each player-initiated bilateral is +1 LLM call).
- UX clarity — the player might over-trigger conversations and get lost.
  Cap at 2 per dimension; show a remaining-quota chip.

---

## C. Time limit / in-game days

**Intent.** Visible timer and progress bar; *2 real minutes = 1 in-game day*;
60-day deadline. The deadline drives drama.

### Data model

```python
"game_started_at": float,         # time.time() at init_game
"in_game_day": int,                # derived: int((now - start) / 120) + 1
"deadline_day": 60,
```

### Implementation

- `st.fragment` (Streamlit ≥ 1.33) **or** a simple "refresh every minute"
  pattern via `st.empty()` + `time.sleep()` in a fragment. We're on
  Streamlit 1.32 today, so the simplest path is a fragment-less refresh
  triggered by a `st.button("⏱ tick")` or auto-rerun via
  `st.rerun()` after each player action — computing the in-game day at the
  top of every render.
- Show a `st.progress(in_game_day / deadline_day, text="Day X / 60")` at the
  top of the game header.
- When `in_game_day >= deadline_day` and the deal isn't passed, force the
  outcome screen with `lose` and `detail = "Deadline reached without a deal."`

### Integration points

- `ensure_state()` — add `game_started_at = time.time()` in `init_game`.
- `render_game_header(stage)` — compute and display the day count.
- `_advance_round2_dimension` and `_advance_round3_dimension` — if
  deadline passes mid-round, call `resolve_game_outcome` early.

### Risks

- Players hate timers that pressure without warning — give them a `Pause`
  button (Pause stops the day counter; useful in classroom settings).
- Pro models are slower → fewer in-game days per real minute → feels
  weirdly different across model choices. Either tie the day-rate to the
  model, or document that 2-min-per-day is calibrated for Flash-Lite.

---

## D. Community + Informal Sector alliance mechanic

**Intent.** The Community Leader and Informal Sector Worker can *form an
alliance*; once allied, their satisfaction and votes correlate, and they
get a small joint "ally bonus" on overlapping dimensions
(`livelihoods`, `community_health_protections`).

### Data model

```python
"alliances": [
    {"members": ["community_member", "informal_sector_worker"],
     "formed_at_stage": "round2_table", "strength": 0.7}
]
```

### Mechanics

- The Community Leader gets a "🤝 Propose alliance with Workers" button
  during Round 2 reply forms when those two are co-present on a dimension.
- On agreement, both stakeholders' `_role_signal` returns a *blended*
  satisfaction (own × 0.7 + ally × 0.3). Forces the AI to vote consistently
  with the ally's strong signal.
- A failed alliance proposal counts as a soft negative for the rejecting
  side's satisfaction.

### Prompt design

When the alliance is active, add a line to both members' proposal prompts:
*"You are publicly allied with {ally_name} on this dimension. Do not
contradict their headline asks; press for joint gains."*

### Integration points

- New `alliances.py` with `propose(a, b)`, `is_allied(a, b)`,
  `blended_signal(role)`.
- Update `_role_signal()` to consult `alliances.blended_signal`.
- Add the proposal button to `render_round2_table` and `render_round3`.

### Risks

- Two-stakeholder alliances are simple; if the spec expands to multi-way
  alliances, the satisfaction blending needs a graph-style aggregation.

---

## E. Real-time negotiation coaching

**Intent.** A teaching layer that watches the player's moves and gives tips
("Tip: ask what matters most to the other party first").

### Architecture

- New `coach.py`:
  - `analyse_move(player_text, dimension, thread) -> Optional[Tip]`
  - Implemented as a *separate* LLM call (cheap, uses the same backend)
    with a small prompt that returns either `None` or a 1-sentence tip
    using one of the CaSiNo strategy labels.
- Render the tip in the Round 2 reply panel: `st.info("💡 Coach: …")`.

### Integration points

- After every `_submit_dimension_reply`, fire `coach.analyse_move` async
  (defer it via the existing busy-state pattern).
- Save tips in `st.session_state.coach_tips` for the outcome review.

### Risks

- Adds 1 LLM call per player turn → cost.
- Tips can be annoying — gate by a `setup.show_coach = True` toggle, and
  cap to at most one tip every 3 turns.
- Pedagogically interesting: the tip set should be drawn from CaSiNo's
  9 strategy labels (already loaded by `training_loader.py`).

---

## F. Faithful draft-proposal synthesis

**Intent.** Today `_synthesize_dimension_proposal` summarises one
dimension's thread into 1–3 sentences. The supervisor wants the final
proposal text to reflect *every* concrete point agreed in the
back-and-forth, not just the last player utterance.

### Approach

1. After each dimension's thread closes, run a *structured* extraction:
   call the LLM with a JSON schema like
   ```json
   {"commitments": [{"actor": "...", "what": "...", "by_when": "..."}],
    "open_questions": ["..."]}
   ```
2. Render each commitment as a bullet in the proposal card for that
   dimension, instead of one flowing paragraph.
3. Final draft proposal: a bullet list per dimension.

### Integration points

- Replace `_synthesize_dimension_proposal` with
  `_extract_commitments_for(dimension)` returning a list of dicts.
- Update `render_proposal_card` to render bullets when the data is
  structured.

### Risks

- Structured-output reliability — Gemini Flash-Lite usually obeys JSON
  schemas but stray text happens. Use `_safe_parse_json` + a re-prompt
  fallback (already in this codebase pattern).

---

## G. True "Back" button on every screen

**Intent.** Player can navigate to the previous step (e.g., re-read role
reveal, re-do Round 2 bids).

### Architecture

State snapshot pattern:

```python
# In ensure_state():
"history": []  # list of (stage, snapshot_dict)

# On every stage transition:
st.session_state.history.append(
    (current_stage, copy.deepcopy(serialisable_state()))
)

# "Back" button:
def back():
    if not st.session_state.history: return
    stage, snap = st.session_state.history.pop()
    apply_snapshot(snap)
    st.session_state.stage = stage
    st.rerun()
```

`serialisable_state()` returns a dict of all `st.session_state` keys *except*
the SDialog `runtime` object (which is process-bound and shouldn't be deep-
copied).

### Integration points

- Add a *sidebar* "← Back" button that calls `back()`.
- Snapshot in the existing `_defer` / stage-transition points.

### Risks

- Going back across an LLM-call boundary needs to either discard the
  generated turn or replay it; document which.
- Memory — deep-copying state every step is fine for a single game but
  blows up if the user plays for hours. Cap the history to 20 entries.

---

## H. Conversation summary in the proposal (one-line "based on" notes)

**Intent.** Instead of pasting full transcripts of bilateral conversations,
the draft proposal carries a single sentence: *"Based on the following
conversations: Stakeholder A spoke with Stakeholder B."*

### Approach

- Combines outputs of A + F: bilaterals each produce a single summary
  line; the final proposal's "rationale" section enumerates them.
- Add a new `"rationale"` block under `render_proposal_card`.

This is the lightest-weight feature in the spec; it falls out for free once
A (background bilaterals) is implemented.

---

## Build order recommendation

If a future session wants to build these, the dependency-minimising order is:

1. **F. Faithful proposal synthesis** (foundation for accurate drafts;
   no new mechanics, prompt + render only).
2. **A. Background AI ↔ AI conversations** (introduces `bilaterals.py`).
3. **H. Conversation summary** (free, builds on A).
4. **B. Player-directed conversation mechanic** (reuses A's plumbing).
5. **C. Time limit** (independent; can land any time).
6. **D. Alliance mechanic** (independent; needs UI work but no LLM
   gymnastics).
7. **E. Coaching** (independent; adds one LLM call per move).
8. **G. Back button** (last — touches every stage transition).

Each section above is self-contained enough to be a small project on its own.
