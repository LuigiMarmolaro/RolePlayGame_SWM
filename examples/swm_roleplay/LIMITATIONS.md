# LIMITATIONS & Configuration — City X Negotiation Game

This file documents *how* the game is configured today, *what to change in the
code* to swap pieces out, *what it costs to run*, and *which features are
planned but not yet built*. Read this before deploying or extending the game.

---

## 1. Which AI model is being used (and how to change it)

The game uses any SDialog-supported chat model. The model is picked **per
session** from the setup screen's dropdown — there is no hardcoded model.

- **Default at top of dropdown:** `google:gemini-2.5-flash-lite`
- **Curated list** (file: `streamlit_app.py`, constant `MODEL_OPTIONS`):
  - `google:gemini-2.5-flash-lite` — fastest & cheapest, recommended
  - `google:gemini-2.5-flash` — balanced quality
  - `google:gemini-2.5-pro` — best reasoning (requires higher billing tier)
  - `google:gemini-2.0-flash` — older fallback
  - `ollama:qwen2.5:latest` — runs locally, no API key needed
  - `openai:gpt-4.1-mini` / `openai:gpt-4o-mini` — requires `OPENAI_API_KEY`
  - `Custom` — paste any SDialog `backend:model` string

### How to add / remove / re-order models

Edit the `MODEL_OPTIONS` list in `streamlit_app.py`. Each entry is a tuple
`(value, display_label)`. The first entry is the default.

### How models authenticate

Resolved by the model prefix:

| Prefix | Required env var | Notes |
|---|---|---|
| `google:` (API-key mode) | `GOOGLE_API_KEY` | From AI Studio, on a billing-enabled GCP project. |
| `google:` (Vertex/ADC) | `GOOGLE_APPLICATION_CREDENTIALS` → service-account JSON in `keys/`. | Auto-loaded by `keys_loader.py`. Vertex AI API must be enabled on the project. |
| `openai:` | `OPENAI_API_KEY` | |
| `anthropic:` | `ANTHROPIC_API_KEY` | |
| `ollama:` | none | Needs a local Ollama daemon. |

Drop a Google service-account JSON into `keys/` and the game prefers ADC/Vertex
automatically (banner on the setup screen confirms). With no service-account
JSON, the setup screen shows an API-key text field for the chosen provider.

---

## 2. How to add or modify scenarios and stakeholders

The scenario is **plain JSON** — no code changes needed for content edits.

- `city_x_scenario.json` — the public scenario:
  - `stakeholders` — list of 6 roles. Each has `id`, `display_name`,
    `public_profile` (title, background, goals, opening position),
    `private_info`, `negotiation` (minimum_requirements, red_lines,
    minimum_thresholds, BATNA).
  - `proposal_dimensions` — the 6 dimensions (2 pre-filled `core_action`/
    `timeline`, 4 negotiable).
  - `events` — surprise events injected mid-game.
- `city_x_game_rules.json` — *hidden* rules kept separate so agents never see
  them: outcome thresholds (≥4 endorsements = win, 3 = partial, ≤2 = lose).
- `relationships.py` — pairwise relationship matrix
  (`RELATIONS[(role_a, role_b)] = {relation, power, topics, forbidden_asks}`)
  AND per-role/per-dimension input hints (`_ROLE_DIM_HINTS`).
  Edit here when adding a stakeholder or a dimension.

### Recipe — add a new stakeholder

1. Add an entry under `stakeholders[]` in `city_x_scenario.json` (full
   schema: see existing entries).
2. Add the role id to `ROUND1_ORDER` and `REACTION_PRIORITY` in
   `streamlit_app.py` (so it joins the speaking order and the per-dimension
   responder lookup).
3. Add a colour/emoji to `STAKEHOLDER_THEME` in `ui/theme.py`.
4. Add an avatar look to `ROLE_LOOK` in `ui/sprites.py`.
5. Add relationships for the new role to `relationships.py`.

### Recipe — swap the scenario for a different city/topic

Replace `city_x_scenario.json` with your own JSON of the same shape and re-run.
The engine is scenario-agnostic; nothing in `src/sdialog/` needs to change.

---

## 3. API keys, costs and rate limits

### Google Gemini (recommended)

- **API-key mode (Gemini API via AI Studio)** — usage bills the GCP billing
  account linked to the project the key belongs to. Free tier exists but has
  tight RPM/RPD limits; for any real play you need to be on **Paid Tier 1**
  (link a billing account to the project).
- **Vertex AI mode (service account in `keys/`)** — auto-selected when a
  service-account JSON is present. Requires:
  - **Vertex AI API enabled** on the project (Cloud Console → APIs &
    Services → Library → Vertex AI API → Enable).
  - The service account needs the **Vertex AI User** role
    (`roles/aiplatform.user`) on the project.

### Ballpark cost per session

A full play (≈40 LLM calls × ~1.5 KB context each, with the new background
+ skills + relationship blocks):

| Model | Approx. cost per full session | Sessions on $50 of GCP credit |
|---|---|---|
| `gemini-2.5-flash-lite` | ~$0.05 – $0.15 | 300+ |
| `gemini-2.5-flash` | ~$0.15 – $0.40 | 120+ |
| `gemini-2.5-pro` | ~$1 – $2 | 25–50 |

Prices change; verify on `cloud.google.com/vertex-ai/generative-ai/pricing`.

### Rate limits

- Free Tier: very tight; one game can trip 429s.
- Paid Tier 1 with Flash-Lite: effectively unlimited for this game's load.
- Pro on Tier 1: lowest RPM of the family; can throttle mid-round.

Set a **budget alert** in Cloud Console → Billing → Budgets to avoid surprises.

---

## 4. Deploying to the cloud

The game is a Streamlit app — any Streamlit host works. Two practical options:

### Option A — Streamlit Community Cloud (free for public apps)

1. Push the repo to a public GitHub repository.
2. Connect at `share.streamlit.io`.
3. Set the main file to `examples/swm_roleplay/streamlit_app.py`.
4. Add **secrets** (`Settings → Secrets`):
   ```toml
   GOOGLE_API_KEY = "paste-your-key-here"
   # or for Vertex: paste the service-account JSON content
   ```
5. The runtime reads `os.environ` — `GOOGLE_API_KEY` and friends from secrets
   are exposed automatically.

### Option B — Google Cloud Run (uses your GCP credit directly)

1. `gcloud builds submit --tag gcr.io/<PROJECT>/cityx` (Streamlit Dockerfile).
2. `gcloud run deploy cityx --image gcr.io/<PROJECT>/cityx --region us-central1`.
3. Attach the same service account as the SA in `keys/` (no JSON file
   needed in the container — Cloud Run mounts ADC automatically).
4. Bills the same project as the rest of your Gemini calls.

### Things to remember when deploying

- **Never commit `keys/*.json` or any API key.** Add `keys/` and `.env` to
  `.gitignore`.
- For Streamlit Cloud, `langchain-google-vertexai` requires the SA content
  pasted into Streamlit secrets and the env var to point at a tmpfile —
  Streamlit Cloud's "service account" pattern is well documented.
- The numpy-vs-anaconda issue you may hit locally is environment-specific;
  on Streamlit Cloud the venv is fresh and `requirements.txt` is honoured.

---

## 5. Teaching the agents a discussion style (few-shot vs. fine-tuning)

Agent behaviour is steered by **prompt + examples**, not by Python state
machines. There are three escalating ways to teach the agents a style:

### A. Few-shot examples (the default — already wired in)

Drop JSONL files in `training/frustration/` (see that folder's `README.md`
for the schema). When the seriousness signal trips, up to 6 examples are
injected into the prompt with strict "copy form, not content" rules. The
model then produces its own variant — different every turn. **Cost: 0**;
just edit the JSONL.

Similar pattern is used for general negotiation moves via
`training_loader.py` (CaSiNo strategy taxonomy + one example per move).

### B. RAG over a bigger corpus (not yet wired)

If you want examples *retrieved* by similarity to the player's last move
(instead of always the same few-shot pool), the path is:

1. Use `text-embedding-004` (or any Gemini embedding model) to embed your
   corpus into a local vector store (one JSON file is fine for ≤ 10k
   examples).
2. At each agent turn, embed the player's text + dimension and pick the
   top-3 nearest examples to inject.

`google.genai`'s embeddings API is one line to call; no extra deps needed.

### C. Fine-tuning Gemini on Vertex AI (recommended for a permanent style)

Vertex AI supports **supervised tuning** of Gemini Flash-Lite / Flash. The
model "learns" your style permanently — no prompt overhead after.

**Format:** JSONL, one example per line:
```json
{"messages": [
  {"role": "user",  "content": "..."},
  {"role": "model", "content": "..."}
]}
```
≥ 100 examples is the recommended minimum.

**Steps (on the same GCP project as the rest of the game):**

1. Save your `.jsonl` to a Cloud Storage bucket (`gsutil cp ...`).
2. Cloud Console → **Vertex AI → Tuning → Create tuned model**.
   - Base model: `gemini-2.5-flash-lite`.
   - Training data: the bucket URL.
3. Tuning runs as a Vertex AI job; cost is a few dollars (well within
   the $50 credit) for a few hundred examples.
4. When done, Vertex gives you a tuned-model id like
   `projects/<PROJECT>/locations/<REGION>/endpoints/<ID>`.
5. Add that id to the `MODEL_OPTIONS` list in `streamlit_app.py` under the
   `google:` prefix. Players can then pick the tuned model on the setup
   screen.

**When to fine-tune vs. stick with few-shot:**

| Need | Use |
|---|---|
| One specific behavioural trait (e.g. negotiator frustration) | Few-shot (already wired) |
| A coherent personality across all turns | Fine-tune |
| Domain-specific vocabulary the base model lacks | Fine-tune |
| Just adding more examples once in a while | Few-shot (cheaper, no job) |

## 6. Future Ideas (not yet implemented)

Tracked in `FUTURE_FRAMEWORK.md`. Short summary of what's planned but not in
code yet:

- **Background AI ↔ AI conversations** — stakeholders talk to each other
  off-stage; transcripts are summarised into the draft proposal.
- **Player-directed conversation mechanic** — the player can ask one
  stakeholder to go talk to another.
- **Time-limit & in-game days** — visible timer mapping real minutes to
  scenario days, with a 60-day deadline.
- **Community + Informal Sector alliance mechanic** — explicit ally support
  the Community Leader can mobilise.
- **Real-time negotiation coaching** — a teaching layer that tips the
  player after weak moves.
- **True "Back" button** — proper state snapshot/restore across stages.
- **Faithful draft-proposal synthesis** — fully reflect *every* agreed item
  from the dimension threads, not just the latest player text.

See `FUTURE_FRAMEWORK.md` for the architectural sketch of each.

---

## 7. Known small limitations today

- Streamlit reruns the whole script on every interaction → one-shot
  animations (XP burst, level-up) feel janky, so we deliberately avoid them.
- The AI's output quality depends heavily on the chosen model; small local
  models (qwen2.5) are weaker on dimension-specific reasoning.
- `transformers` is installed as a transitive dep of SDialog and Streamlit's
  file watcher noisily probes it at startup (`torchvision` warning). Harmless;
  silence with `streamlit run … --server.fileWatcherType=none`.
- Game logic uses rule thresholds + LLM-as-judge, not a formal game-theoretic
  solver. A "weak passed" outcome (passes by endorsements but with poor
  scorecard) is a feature, not a bug.
