# City X Negotiation Game

This repository contains the Streamlit prototype for the City X solid waste management negotiation game, built on top of the SDialog toolkit.

The game lets one human player choose a stakeholder role while AI agents play the remaining stakeholders. The negotiation is structured around opening positions, proposal-building across four negotiated dimensions, stakeholder flagging, Round 3 revisions, a final vote, and an outcome scorecard.

## Main Files

- `examples/swm_roleplay/streamlit_app.py`: Streamlit UI and game orchestration.
- `examples/swm_roleplay/city_x_scenario.json`: public scenario, role cards, relationships, red lines, and negotiation content.
- `examples/swm_roleplay/city_x_game_rules.json`: hidden thresholds used for scoring and debrief logic.
- `examples/swm_roleplay/simulate_play.py`: browserless simulation harness used for automated playtesting.
- `examples/swm_roleplay/simulations/`: saved playthrough JSON files and aggregate summary.
- `src/sdialog/roleplay.py`: scenario loader that converts JSON stakeholders into SDialog personas and agents.
- `src/sdialog/roleplay_engine.py`: game-state helpers, proposal state, voting, and outcome resolution.
- `src/sdialog/agents.py`: SDialog agent implementation used by the role-play agents.
- `SDIALOG_README.md`: original SDialog toolkit README.

## Install

Use Python 3.12 if possible.

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
pip install streamlit
```

## Run the Game

```bash
source .venv/bin/activate
streamlit run examples/swm_roleplay/streamlit_app.py
```

Then open the local Streamlit URL shown in the terminal.

## AI Authentication

Do not commit API keys or service-account files to GitHub.

The app supports three practical modes:

- Google Vertex / ADC: create a local folder named `keys/` at the repo root or inside `examples/swm_roleplay/`, then place your Google service-account JSON there. The app auto-loads it through `examples/swm_roleplay/keys_loader.py`. This folder is ignored by Git.
- Gemini API key: set `GOOGLE_API_KEY` in your shell before running Streamlit, or paste it in the setup screen. Do not write it into committed code.
- Ollama local model: install Ollama and select an `ollama:` model in the setup screen. This avoids cloud API usage.

Example environment-variable setup:

```bash
export GOOGLE_API_KEY="paste-key-here"
streamlit run examples/swm_roleplay/streamlit_app.py
```

## Run Automated Simulations

The harness plays complete games without opening the browser and saves JSON transcripts.

```bash
source .venv/bin/activate
python examples/swm_roleplay/simulate_play.py
```

The default harness model is `google:gemini-2.5-flash-lite`. Results are saved in:

```text
examples/swm_roleplay/simulations/
```
