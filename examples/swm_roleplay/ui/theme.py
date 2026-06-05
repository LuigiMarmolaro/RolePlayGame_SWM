"""Single source of truth for palette, stakeholder identity, and global CSS.

Drop-in replacement for ``examples/swm_roleplay/ui/theme.py``.

Changes vs upstream:
- Added animated aurora field on .stApp (cxAurora keyframes).
- Added .cx-chrome top bar styling for the SWM wordmark chrome.
- Added .wm-bubble-row + .wm-bubble-av + .wm-typing for the new transcript
  bubbles that include an inline avatar + typing-dot animation.
- Added .wm-pill v-green / v-yellow / v-red / v-neutral as canonical names
  (kept alongside the existing styles).
- Added wmTypingDot, wmSpeakDot, cxAurora, cxLogoIn, cxDot keyframes.

Stakeholder palette + colors are unchanged.
"""
from typing import Dict

# --- Core palette ---------------------------------------------------------
PALETTE: Dict[str, str] = {
    "olive_deep": "#3f6b3c",
    "olive": "#5e7d4f",
    "sage": "#a8aa9b",
    "stone": "#d8d5cc",
    "paper": "#c89c62",
    "kraft": "#8e6b3f",
    "charcoal": "#2a2d26",
    "cream": "#f7f3e8",
    "danger": "#b76554",
    "amber": "#c89c62",
}

# --- Stakeholder identity (the ONLY place colors/emoji are defined) -------
STAKEHOLDER_THEME: Dict[str, Dict[str, str]] = {
    "national_government": {"emoji": "🏛️", "color": "#245c4a", "bg": "#eef8f1", "short": "National"},
    "municipal_government": {"emoji": "🏙️", "color": "#2f6f5e", "bg": "#effaf6", "short": "Municipal"},
    "private_sector_company": {"emoji": "💼", "color": "#7a5a1f", "bg": "#f8f4e8", "short": "Private"},
    "ngo_civil_society": {"emoji": "🌿", "color": "#1f7a4c", "bg": "#edf9f1", "short": "NGO"},
    "community_member": {"emoji": "🏘️", "color": "#3d6f59", "bg": "#f3fbf4", "short": "Community"},
    "informal_sector_worker": {"emoji": "♻️", "color": "#157347", "bg": "#edf9f0", "short": "Workers"},
}

_DEFAULT_ROLE = {"emoji": "👤", "color": "#475569", "bg": "#f8fafc", "short": "Role"}


def role_theme(role_id: str) -> Dict[str, str]:
    """Resolve a stakeholder's visual identity (never raises)."""
    return STAKEHOLDER_THEME.get(role_id, _DEFAULT_ROLE)


_EFFECTS_CSS = r"""
/* ===== Effects pack (claude_design/effects) ===== */
/* Background delivered as a fixed, behind-content layer (no overflow clip). */
.cx-bg-fx {
    position: fixed; inset: 0; z-index: 0; pointer-events: none; overflow: hidden;
}
.cx-bg-grain {
    position: absolute; inset: 0; opacity: 0.30; mix-blend-mode: multiply;
    background-image:
        radial-gradient(circle at 1px 1px, rgba(72,66,43,0.05) 1px, transparent 1.5px),
        radial-gradient(circle at 3px 4px, rgba(72,66,43,0.04) 1px, transparent 1px);
    background-size: 6px 6px, 11px 9px;
}
.cx-bg-conveyor {
    position: absolute; left: 0; right: 0; bottom: 0; height: 80px; overflow: hidden;
    background: linear-gradient(180deg, transparent 0%, rgba(142,107,63,0.12) 100%);
}
.cx-bg-conveyor::before {
    content: ""; position: absolute; left: -10%; right: -10%; bottom: 0; height: 100%;
    background:
        radial-gradient(circle at 10% 90%, rgba(94,125,79,0.18) 0%, transparent 6%),
        radial-gradient(circle at 30% 88%, rgba(142,107,63,0.14) 0%, transparent 5%),
        radial-gradient(circle at 55% 92%, rgba(94,125,79,0.16) 0%, transparent 6%),
        radial-gradient(circle at 78% 87%, rgba(142,107,63,0.12) 0%, transparent 5%),
        radial-gradient(circle at 92% 91%, rgba(94,125,79,0.14) 0%, transparent 6%);
    animation: cxConveyor 40s linear infinite;
}
@keyframes cxConveyor { 0% { transform: translateX(0); } 100% { transform: translateX(-12%); } }
.cx-particle {
    position: absolute; bottom: -40px; width: 16px; height: 16px; opacity: 0;
    animation: cxFloatUp linear infinite; will-change: transform, opacity;
}
.cx-particle svg { display: block; width: 100%; height: 100%; }
@keyframes cxFloatUp {
    0%   { transform: translate(0,0) rotate(0); opacity: 0; }
    10%  { opacity: 0.6; }
    50%  { transform: translate(20px,-50vh) rotate(180deg); opacity: 0.7; }
    90%  { opacity: 0.45; }
    100% { transform: translate(-20px,-110vh) rotate(360deg); opacity: 0; }
}
.cx-sparkle {
    position: absolute; width: 6px; height: 6px; opacity: 0; border-radius: 50%;
    background:
        linear-gradient(45deg, transparent 40%, #fff7d4 50%, transparent 60%),
        linear-gradient(-45deg, transparent 40%, #fff7d4 50%, transparent 60%);
    box-shadow: 0 0 8px rgba(255,247,212,0.8);
    animation: cxTwinkle 4s ease-in-out infinite;
}
@keyframes cxTwinkle {
    0%,100% { opacity: 0; transform: scale(0.5); }
    50%     { opacity: 0.9; transform: scale(1.4); }
}
/* ---- Animation library (inert until a cx- class is applied) ---- */
@keyframes cxConfettiPop {
    0%  { opacity: 0; transform: translate(0,0) rotate(0) scale(0.2); }
    20% { opacity: 1; }
    100%{ opacity: 0; transform: translate(var(--dx),var(--dy)) rotate(var(--rot)) scale(1); }
}
.cx-confetti { position: relative; display: inline-block; width: 0; height: 0; }
.cx-confetti i {
    position: absolute; left: 0; top: 0; width: 8px; height: 14px; border-radius: 2px;
    animation: cxConfettiPop 1.2s cubic-bezier(.22,1,.36,1) forwards;
}
.cx-confetti i:nth-child(1)  { background:#3f6b3c; --dx:-60px;  --dy:-80px;  --rot:280deg; }
.cx-confetti i:nth-child(2)  { background:#c89c62; --dx:40px;   --dy:-100px; --rot:360deg; animation-delay:.04s; }
.cx-confetti i:nth-child(3)  { background:#5e7d4f; --dx:80px;   --dy:-60px;  --rot:200deg; animation-delay:.08s; }
.cx-confetti i:nth-child(4)  { background:#b76554; --dx:-90px;  --dy:-40px;  --rot:420deg; animation-delay:.02s; }
.cx-confetti i:nth-child(5)  { background:#8e6b3f; --dx:20px;   --dy:-120px; --rot:540deg; animation-delay:.06s; }
.cx-confetti i:nth-child(6)  { background:#157347; --dx:-30px;  --dy:-110px; --rot:320deg; animation-delay:.10s; }
.cx-confetti i:nth-child(7)  { background:#c89c62; --dx:100px;  --dy:-30px;  --rot:180deg; animation-delay:.12s; }
.cx-confetti i:nth-child(8)  { background:#3f6b3c; --dx:-110px; --dy:-90px;  --rot:460deg; animation-delay:.14s; }
.cx-confetti i:nth-child(9)  { background:#1f7a4c; --dx:60px;   --dy:-120px; --rot:600deg; animation-delay:.16s; }
.cx-confetti i:nth-child(10) { background:#245c4a; --dx:-70px;  --dy:-130px; --rot:240deg; animation-delay:.18s; }
.cx-confetti i:nth-child(11) { background:#c89c62; --dx:30px;   --dy:-70px;  --rot:380deg; animation-delay:.20s; }
.cx-confetti i:nth-child(12) { background:#5e7d4f; --dx:-50px;  --dy:-150px; --rot:720deg; animation-delay:.22s; }
@keyframes cxStampThump {
    0%  { transform: scale(2)    rotate(-12deg); opacity: 0; }
    50% { transform: scale(0.95) rotate(-6deg);  opacity: 1; }
    65% { transform: scale(1.05) rotate(-6deg);  opacity: 1; }
    100%{ transform: scale(1)    rotate(-6deg);  opacity: 1; }
}
.cx-stamp {
    display: inline-block; padding: 8px 16px; border: 3px solid #b76554;
    border-radius: 4px; color: #b76554; font-family: var(--font-display, Georgia, serif);
    font-size: 14px; font-weight: 700; letter-spacing: 0.18em; text-transform: uppercase;
    background: rgba(247,243,232,0.4);
    animation: cxStampThump 0.5s cubic-bezier(.34,1.56,.64,1) both;
}
.cx-stamp.green { border-color: #3f6b3c; color: #3f6b3c; }
@keyframes cxGlowPulse {
    0%,100% { box-shadow: 0 0 0 0 rgba(63,107,60,0.55), 0 8px 18px rgba(63,107,60,0.24); }
    50%     { box-shadow: 0 0 0 8px rgba(63,107,60,0),  0 12px 24px rgba(63,107,60,0.36); }
}
.cx-anim-glow { animation: cxGlowPulse 2s ease-in-out infinite; }
.cx-meter-shimmer { position: relative; overflow: hidden; }
.cx-meter-shimmer::after {
    content: ""; position: absolute; inset: 0; transform: translateX(-100%);
    background: linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.5) 50%, transparent 100%);
    animation: cxMeterShimmer 2.5s linear infinite;
}
@keyframes cxMeterShimmer { 0% { transform: translateX(-100%); } 100% { transform: translateX(200%); } }
@keyframes cxScreenShake {
    0%,100% { transform: translate(0,0); } 20% { transform: translate(4px,-2px); }
    40% { transform: translate(-5px,2px); } 60% { transform: translate(3px,2px); }
    80% { transform: translate(-2px,-1px); }
}
.cx-anim-shake { animation: cxScreenShake 0.55s cubic-bezier(.36,.07,.19,.97); }
@keyframes cxCardFlip {
    0%  { transform: perspective(800px) rotateY(180deg); opacity: 0; }
    60% { opacity: 1; }
    100%{ transform: perspective(800px) rotateY(0deg); opacity: 1; }
}
.cx-anim-flip { animation: cxCardFlip 0.8s cubic-bezier(.22,1,.36,1) both; }
@keyframes cxPopBubble {
    0%  { opacity: 0; transform: scale(0.4) translateY(8px); }
    60% { opacity: 1; transform: scale(1.08) translateY(0); }
    100%{ opacity: 1; transform: scale(1) translateY(0); }
}
.cx-anim-pop { animation: cxPopBubble 0.45s cubic-bezier(.34,1.56,.64,1) both; }
@keyframes cxLevelUp {
    0%  { opacity: 0; transform: translateY(20px) scale(0.7); }
    15% { opacity: 1; transform: translateY(0) scale(1.2); }
    30% { transform: translateY(0) scale(1); }
    70% { opacity: 1; }
    100%{ opacity: 0; transform: translateY(-30px) scale(1); }
}
.cx-level-up {
    font-family: var(--font-display, Georgia, serif); font-size: 32px; font-weight: 700;
    font-style: italic; color: #3f6b3c;
    text-shadow: 0 0 12px rgba(255,220,130,0.7), 0 4px 12px rgba(63,107,60,0.5);
    animation: cxLevelUp 2.2s ease-out forwards;
}
@media (prefers-reduced-motion: reduce) {
    .cx-bg-fx, .cx-particle, .cx-sparkle, .cx-bg-conveyor::before,
    .cx-anim-glow, .cx-meter-shimmer::after { animation: none !important; }
}
"""


def css() -> str:
    """Return the full global stylesheet (base theme + gamified additions)."""
    p = PALETTE
    # Web-font pairing from the City X design system (Newsreader / Public Sans /
    # JetBrains Mono). Built as one line via concatenation so no source line
    # exceeds the lint limit while the emitted @import stays a single statement.
    font_import = (
        '@import url("https://fonts.googleapis.com/css2?'
        'family=Newsreader:opsz,wght@6..72,400;6..72,600;6..72,700&'
        'family=Public+Sans:ital,wght@0,400;0,600;0,700;1,400&'
        'family=JetBrains+Mono:wght@400;600&display=swap");'
    )
    # Effects pack (claude_design/effects). Plain string (literal braces) so it
    # is injected verbatim into the f-string below without brace-escaping.
    # NOTE: the pack's .cx-bg-game uses overflow:hidden which would clip
    # Streamlit's scroll, so the background is delivered as a fixed,
    # behind-content .cx-bg-fx layer instead.
    effects_css = _EFFECTS_CSS
    return f"""
<style>
{font_import}
:root {{
    --wm-font-display: "Newsreader", Georgia, "Times New Roman", serif;
    --wm-font-body: "Public Sans", "Source Sans 3", system-ui,
        -apple-system, "Segoe UI", Roboto, sans-serif;
    --wm-font-mono: "JetBrains Mono", ui-monospace, "SF Mono", Menlo, monospace;
    --font-display: var(--wm-font-display);
    --font-body: var(--wm-font-body);
    --wm-olive-deep: {p['olive_deep']};
    --wm-olive: {p['olive']};
    --wm-sage: {p['sage']};
    --wm-stone: {p['stone']};
    --wm-paper: {p['paper']};
    --wm-kraft: {p['kraft']};
    --wm-charcoal: {p['charcoal']};
    --wm-cream: {p['cream']};
    --wm-danger: {p['danger']};
}}

/* --- App field: animated olive aurora over warm gradient --- */
.stApp {{
    position: relative;
    background:
        radial-gradient(ellipse at 50% 0%, rgba(255,253,225,0.60), transparent 55%),
        radial-gradient(circle at 88% 92%, rgba(120,170,95,0.30), transparent 55%),
        radial-gradient(circle at 8% 90%, rgba(150,196,110,0.24), transparent 50%),
        linear-gradient(145deg,
            #f6ef9e 0%, #e3ec85 28%, #c7e07a 52%,
            #aed47e 76%, #cfe78a 100%);
    background-size: 100% 100%, 100% 100%, 100% 100%, 300% 300%;
    animation: cxShades 30s ease-in-out infinite alternate;
}}
@keyframes cxShades {{
    0%   {{ background-position: 0 0, 0 0, 0 0, 0% 50%; }}
    50%  {{ background-position: 0 0, 0 0, 0 0, 100% 50%; }}
    100% {{ background-position: 0 0, 0 0, 0 0, 50% 100%; }}
}}
/* Aurora sits BEHIND content: absolute (not fixed) + negative z-index so it
   never overlays or clips Streamlit's scrollable view. */
.stApp::before,
.stApp::after {{
    content: ""; position: absolute; inset: 0; pointer-events: none; z-index: 0;
    background:
        radial-gradient(circle at 25% 65%, rgba(246,239,158,0.45), transparent 40%),
        radial-gradient(circle at 75% 35%, rgba(174,212,126,0.40), transparent 36%);
    filter: blur(28px);
    animation: cxAurora 17s ease-in-out infinite alternate;
}}
/* Outer wrappers stay transparent so the animated gradient shows around the
   content; the block-container is ONE big paper panel that holds all the
   text, so nothing floats and paragraphs share a single box. */
[data-testid="stAppViewContainer"], [data-testid="stMain"],
section.main, .main {{
    position: relative; z-index: 1; background: transparent !important;
}}
.block-container {{
    position: relative; z-index: 1;
    background: rgba(248,245,235,0.78) !important;
    border: 1px solid rgba(94,125,79,0.18);
    border-radius: 20px;
    padding: 22px 30px 34px !important;
    margin-top: 8px;
    box-shadow: 0 18px 40px rgba(72,66,43,0.10);
    backdrop-filter: blur(2px);
}}
/* The default Streamlit top bar reads as a solid black strip over the game;
   make it transparent so the aurora shows and it stops overlapping. */
header[data-testid="stHeader"], [data-testid="stHeader"],
[data-testid="stToolbar"] {{
    background: transparent !important; box-shadow: none !important;
}}
/* Our body-font override also hit Streamlit's Material icons, so the sidebar
   collapse control rendered the ligature text "keyboard_double_arrow_left".
   Restore the icon font on all Streamlit icon glyphs. */
[data-testid="stIconMaterial"], span[data-testid="stIconMaterial"],
[data-testid="stSidebarCollapseButton"] span,
[data-testid="baseButton-headerNoPadding"] span,
.material-icons, .material-symbols-rounded, .material-symbols-outlined {{
    font-family: "Material Symbols Rounded", "Material Symbols Outlined",
        "Material Icons" !important;
}}
/* Stop the "Draft proposal so far" expander / select dropdowns from
   overlapping neighbouring blocks. */
[data-testid="stExpander"] {{
    position: relative; z-index: 1; margin: 6px 0;
    background: rgba(247,243,232,0.6); border-radius: 12px;
}}
[data-testid="stExpander"] summary {{ position: relative; z-index: 1; }}
[data-baseweb="popover"], [data-baseweb="menu"] {{ z-index: 9999 !important; }}
/* All loose text lives on the single .block-container panel (above), so we
   do NOT add a second box per element. Widgets that already carry their own
   surface (buttons, inputs, alerts) keep it and must not be re-boxed. */
.block-container [data-testid="stMarkdownContainer"] {{ background: transparent; }}

/* Wave A — Download button readable (was black-on-black). */
[data-testid="stDownloadButton"] button {{
    background: linear-gradient(135deg, var(--wm-olive-deep) 0%, var(--wm-olive) 100%) !important;
    color: #ffffff !important;
    border: 1px solid var(--wm-olive-deep) !important;
    border-radius: 999px !important;
    font-weight: 600 !important;
    box-shadow: 0 10px 22px rgba(63,107,60,0.20);
}}
[data-testid="stDownloadButton"] button:hover {{ color: #ffffff !important; filter: brightness(1.05); }}

/* Per-dimension accent strip — on the RIGHT edge so it doesn't conflict
   with the status colour (which lives on the left border). */
.proposal-box {{ margin-bottom: 14px; position: relative; }}
.proposal-box.dim-financing {{ box-shadow: inset -6px 0 0 #c89c62, 0 14px 30px rgba(72,66,43,0.06); }}
.proposal-box.dim-community_health_protections {{
    box-shadow: inset -6px 0 0 #b76554, 0 14px 30px rgba(72,66,43,0.06);
}}
.proposal-box.dim-livelihoods {{ box-shadow: inset -6px 0 0 #1f7a4c, 0 14px 30px rgba(72,66,43,0.06); }}
.proposal-box.dim-monitoring_and_enforcement {{ box-shadow: inset -6px 0 0 #4a5e8c, 0 14px 30px rgba(72,66,43,0.06); }}

/* "Fixed" pre-set dimensions look visibly locked; the locked style wins
   over the dim accent so they don't visually clash. */
.proposal-box.dim-locked {{
    background: repeating-linear-gradient(135deg,
        rgba(216,213,204,0.55) 0px, rgba(216,213,204,0.55) 8px,
        rgba(236,234,225,0.55) 8px, rgba(236,234,225,0.55) 16px) !important;
    border-style: dashed;
    border-left: 6px solid var(--wm-sage) !important;
    box-shadow: 0 14px 30px rgba(72,66,43,0.06) !important;
    opacity: 0.96;
}}
.dim-locked-chip {{
    display: inline-block; margin-left: 8px; padding: 2px 9px; border-radius: 999px;
    font-size: 11px; font-weight: 700; letter-spacing: .06em;
    background: rgba(168,170,155,0.45); color: #3f3a2c;
    border: 1px solid rgba(94,125,79,0.30);
}}

/* Wave A — Satisfaction label below the meter (agree / partially / disagree). */
.wm-sat-label {{
    display: block; margin-top: 4px; font-size: 11px; font-weight: 700;
    letter-spacing: .04em; text-transform: uppercase;
}}
.wm-sat-label.agrees    {{ color: #2f7a4c; }}
.wm-sat-label.partial   {{ color: #b07a2a; }}
.wm-sat-label.disagrees {{ color: #b76554; }}
.wm-sat-label.absent    {{ color: #7c7666; }}
/* Selectbox closed control — cream paper with charcoal text.
   Keep selects as inputs, not dark buttons, so dropdowns stay readable. */
[data-testid="stSelectbox"] div[data-baseweb="select"] > div {{
    background: rgba(247,243,232,0.96) !important;
    border-color: rgba(94,125,79,0.42) !important;
}}
[data-testid="stSelectbox"] div[data-baseweb="select"] *,
[data-testid="stSelectbox"] div[data-baseweb="select"] svg {{
    color: var(--wm-charcoal) !important;
    -webkit-text-fill-color: var(--wm-charcoal) !important;
    fill: var(--wm-olive-deep) !important;
}}
/* Dropdown OPEN list (and multiselect list, and popover) — cream paper with
   olive hover. Same family as the rest of the game. */
[data-baseweb="popover"] [role="listbox"],
[data-baseweb="menu"] {{
    background: rgba(247,243,232,0.97) !important;
    border: 1px solid rgba(94,125,79,0.30) !important;
    border-radius: 12px !important;
    box-shadow: 0 14px 30px rgba(72,66,43,0.18) !important;
    padding: 4px !important;
}}
[data-baseweb="popover"] [role="option"],
[data-baseweb="menu"] li {{
    color: var(--wm-charcoal) !important;
    border-radius: 8px !important;
    margin: 2px 0 !important;
}}
[data-baseweb="popover"] [role="option"]:hover,
[data-baseweb="popover"] [role="option"][aria-selected="true"],
[data-baseweb="menu"] li:hover {{
    background: rgba(94,125,79,0.16) !important;
    color: var(--wm-olive-deep) !important;
}}
/* Multiselect chips (the selected items shown inside the closed control). */
[data-testid="stMultiSelect"] div[data-baseweb="select"] > div {{
    background: var(--wm-cream) !important;
    border-color: var(--wm-olive) !important;
}}
[data-testid="stMultiSelect"] div[data-baseweb="select"] [data-baseweb="tag"] {{
    background: var(--wm-olive-deep) !important;
    color: #ffffff !important;
    border-radius: 999px !important;
}}
[data-testid="stMultiSelect"] div[data-baseweb="select"] [data-baseweb="tag"] * {{
    color: #ffffff !important;
}}
/* "What do I do here?" popover trigger button + body — themed to match. */
[data-testid="stPopover"] > button,
[data-testid="stPopoverButton"] {{
    background: rgba(247,243,232,0.92) !important;
    color: var(--wm-olive-deep) !important;
    border: 1px solid rgba(94,125,79,0.30) !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
}}
[data-testid="stPopover"] > button:hover,
[data-testid="stPopoverButton"]:hover {{
    background: rgba(94,125,79,0.10) !important;
}}
[data-testid="stPopoverBody"], [data-baseweb="popover"] [data-testid="stPopoverBody"] {{
    background: rgba(247,243,232,0.98) !important;
    border: 1px solid rgba(94,125,79,0.30) !important;
    border-radius: 14px !important;
    color: var(--wm-charcoal) !important;
    padding: 18px 22px !important;
    line-height: 1.5 !important;
}}
[data-testid="stPopoverBody"] p {{ margin: 0 !important; }}

/* Scrolling + visible olive scrollbar across every scrollable container. */
html, body, .stApp,
[data-testid="stAppViewContainer"], [data-testid="stMain"],
section.main, .main {{
    overflow-y: auto !important;
    scrollbar-width: thin;
    scrollbar-color: rgba(94,125,79,0.55) rgba(247,243,232,0.4);
}}
.stApp::-webkit-scrollbar,
[data-testid="stAppViewContainer"]::-webkit-scrollbar,
[data-testid="stMain"]::-webkit-scrollbar,
section.main::-webkit-scrollbar,
.block-container::-webkit-scrollbar {{
    width: 12px;
}}
.stApp::-webkit-scrollbar-track,
[data-testid="stAppViewContainer"]::-webkit-scrollbar-track,
[data-testid="stMain"]::-webkit-scrollbar-track {{
    background: rgba(247,243,232,0.4);
}}
.stApp::-webkit-scrollbar-thumb,
[data-testid="stAppViewContainer"]::-webkit-scrollbar-thumb,
[data-testid="stMain"]::-webkit-scrollbar-thumb {{
    background: rgba(94,125,79,0.55);
    border-radius: 999px;
    border: 2px solid rgba(247,243,232,0.4);
}}
.stApp::-webkit-scrollbar-thumb:hover {{ background: var(--wm-olive-deep); }}
/* Radios + checkboxes — themed colour on the active mark. */
[data-baseweb="radio"] div[role="radio"][aria-checked="true"],
[data-baseweb="checkbox"] div[role="checkbox"][aria-checked="true"] {{
    border-color: var(--wm-olive-deep) !important;
    background: var(--wm-olive-deep) !important;
}}
.stApp::after {{
    background:
        radial-gradient(circle at 60% 80%, rgba(255,250,205,0.42), transparent 36%),
        radial-gradient(circle at 20% 30%, rgba(160,200,118,0.36), transparent 36%);
    animation-duration: 25s; animation-direction: alternate-reverse;
}}
@media (prefers-reduced-motion: reduce) {{
    .stApp, .stApp::before, .stApp::after {{ animation: none !important; }}
}}
.block-container {{ padding-top: 1rem !important; max-width: 1200px; position: relative; z-index: 1; }}

.stApp, .stApp p, .stApp li, .stApp label, .stApp span, .stApp div, .stApp small {{
    color: var(--wm-charcoal);
}}
.stMarkdown, .stMarkdown p, .stMarkdown li, .stMarkdown span {{ color: var(--wm-charcoal) !important; }}
.stApp, .stApp p, .stApp li, .stApp label, .stApp span, .stApp div, .stApp small,
.stMarkdown, [data-testid="stSidebar"] * {{ font-family: var(--wm-font-body); }}
.stApp h1, .stApp h2, .stApp h3, .stApp h4, .round-hdr h3, .t-display {{
    font-family: var(--wm-font-display) !important; letter-spacing: -0.01em;
}}
code, kbd, pre, .t-mono {{ font-family: var(--wm-font-mono); }}
[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, rgba(232,225,210,0.96) 0%, rgba(241,236,225,0.96) 100%);
    border-right: 1px solid rgba(94,125,79,0.16);
}}
[data-testid="stSidebar"] * {{ color: var(--wm-charcoal) !important; }}
[data-testid="stAlertContainer"], [data-testid="stAlertContainer"] * {{ color: var(--wm-charcoal) !important; }}
[data-testid="stAlertContainer"] > div {{
    border-radius: 14px !important;
    border: 1px solid rgba(94,125,79,0.14) !important;
    background: rgba(247,243,232,0.94) !important;
    box-shadow: 0 10px 24px rgba(72,66,43,0.07);
}}
[data-testid="stTextArea"] textarea, [data-testid="stTextInput"] input {{
    color: var(--wm-charcoal) !important;
    -webkit-text-fill-color: var(--wm-charcoal) !important;
    background: rgba(247,243,232,0.95) !important;
    border-radius: 12px !important;
    border: 1px solid rgba(142,107,63,0.22) !important;
}}
[data-testid="stButton"] button {{
    border-radius: 999px !important;
    border: 1px solid rgba(94,125,79,0.18) !important;
    background: linear-gradient(180deg, #f5efe2 0%, #eadfcb 100%) !important;
    color: #4c402a !important;
    font-weight: 600 !important;
    box-shadow: 0 8px 20px rgba(72,66,43,0.08);
    transition: transform .12s ease, box-shadow .12s ease;
}}
[data-testid="stButton"] button:hover {{ transform: translateY(-1px); }}
[data-testid="stButton"] button[kind="primary"] {{
    background: linear-gradient(135deg, var(--wm-olive-deep) 0%, var(--wm-olive) 100%) !important;
    color: #fff !important;
    border-color: var(--wm-olive-deep) !important;
    box-shadow: 0 12px 26px rgba(63,107,60,0.24);
}}

/* --- SWM chrome bar (top of page, optional — render via components.chrome_bar()) --- */
.cx-chrome {{
    position: relative; z-index: 2;
    display: flex; align-items: center; justify-content: space-between;
    padding: 10px 18px; margin: 0 0 16px;
    gap: 16px;
}}
.cx-chrome-logo {{
    display: flex; align-items: center; gap: 10px;
    color: #2a2d26; text-decoration: none;
}}
.cx-chrome-logo .wordmark {{
    font-family: var(--wm-font-display);
    font-size: 22px; font-weight: 700; letter-spacing: -0.01em; line-height: 1;
    color: #2a2d26;
}}
.cx-chrome-logo .wordmark em {{ font-style: italic; color: #3f6b3c; }}
.cx-chrome-logo .tag {{
    font-size: 10.5px; font-weight: 700; letter-spacing: 0.12em;
    text-transform: uppercase; color: #5b4a32; margin-top: 3px; display: block;
}}
.cx-chrome-right {{ display: flex; align-items: center; gap: 14px; font-size: 12.5px; color: #5b4a32; }}
.cx-chip {{
    display: inline-flex; align-items: center; gap: 6px;
    padding: 5px 12px; border-radius: 999px;
    background: rgba(247,243,232,0.85); border: 1px solid rgba(142,107,63,0.22);
    font-weight: 600; font-size: 11.5px; color: #5b4a32;
    box-shadow: 0 4px 12px rgba(72,66,43,0.06);
}}
.cx-chip .dot {{
    width: 8px; height: 8px; border-radius: 50%;
    background: #3f6b3c; animation: cxDot 1.8s ease-out infinite;
}}

/* --- Transcript bubbles (now with inline avatar + typing dots) --- */
.msg-bubble {{
    border-radius: 14px; padding: 12px 15px; margin-bottom: 10px;
    border-left: 5px solid #92a07d; border: 1px solid rgba(94,125,79,0.10);
    background: rgba(247,243,232,0.92); color: var(--wm-charcoal);
    box-shadow: 0 10px 26px rgba(72,66,43,0.06);
    animation: wmFadeIn .35s ease both;
}}
.msg-human {{ background: linear-gradient(180deg,#efe8d7 0%,#faf7ef 100%); border-left-color: var(--wm-paper); }}
.msg-mod {{
    background: linear-gradient(180deg,#e4eadb 0%,#f4f5ee 100%);
    border-left-color: var(--wm-olive); text-align: left;
}}
.wm-bubble-row {{ display: flex; align-items: flex-start; gap: 12px; }}
.wm-bubble-av {{
    flex: 0 0 auto; width: 44px; height: 44px; border-radius: 50%;
    overflow: hidden; box-shadow: 0 6px 14px rgba(72,66,43,0.10);
}}
.wm-bubble-av svg {{ display: block; }}
.wm-mod-av {{
    background: linear-gradient(135deg, var(--wm-olive-deep), var(--wm-olive));
    color: #fff; display: grid; place-items: center; font-size: 22px;
    box-shadow: 0 6px 14px rgba(63,107,60,0.30);
}}
.wm-bubble-body {{ flex: 1; min-width: 0; }}
.wm-bubble-body b {{ font-size: .92rem; }}
.wm-bubble-text {{ margin-top: 4px; line-height: 1.5; font-size: .95rem; }}
.wm-typing {{ display: inline-flex; gap: 4px; align-items: center; padding: 4px 0; }}
.wm-typing span {{
    width: 7px; height: 7px; border-radius: 50%;
    background: var(--dot-color, #5b4a32); opacity: .35;
    animation: wmTypingDot 1.2s ease-in-out infinite;
}}
.wm-typing span:nth-child(2) {{ animation-delay: .15s; }}
.wm-typing span:nth-child(3) {{ animation-delay: .3s; }}

/* --- Proposal / blueprint modules --- */
.proposal-box {{
    border: 1px solid rgba(142,107,63,0.15); border-radius: 16px; padding: 13px 15px;
    background: linear-gradient(180deg, rgba(242,235,220,0.96) 0%, rgba(248,243,232,0.96) 100%);
    margin-bottom: 12px; box-shadow: 0 14px 30px rgba(72,66,43,0.06);
    transition: border-color .4s ease, background .6s ease;
}}
.proposal-green {{
    border-left: 6px solid var(--wm-olive-deep);
    background: linear-gradient(180deg,#edf2e7 0%,#f6f7f1 100%);
    animation: wmSnap .5s ease both;
}}
.proposal-yellow {{
    border-left: 6px solid var(--wm-paper);
    background: linear-gradient(180deg,#f5ecd9 0%,#fbf7ed 100%);
}}
.proposal-red {{
    border-left: 6px solid var(--wm-danger);
    background: linear-gradient(180deg,#f5e8e3 0%,#fbf3ef 100%);
    animation: wmShake .45s ease both;
}}
.proposal-neutral {{
    border-left: 6px solid var(--wm-sage);
    background: linear-gradient(180deg,#f0eee7 0%,#f7f4ec 100%);
}}

/* --- Round header --- */
.round-hdr {{
    background: linear-gradient(135deg, rgba(74,80,66,0.98) 0%, rgba(94,125,79,0.98) 54%, rgba(126,145,101,0.98) 100%);
    color: #fff; border-radius: 18px; padding: 16px 20px; margin-bottom: 14px;
    box-shadow: 0 18px 34px rgba(28,64,46,0.18);
}}
.round-hdr h3, .round-hdr p, .round-hdr span, .round-hdr div {{ color: #fff !important; }}
.round-hdr h3 {{ margin: 0 0 2px 0; }}
.badge {{
    display: inline-block; border-radius: 999px; padding: 3px 10px; font-size: 12px;
    margin: 0 6px 4px 0; background: #e8dfcf; color: #5b4a32;
    border: 1px solid rgba(142,107,63,0.16);
}}

/* --- Game spine (waste-processing pipeline) --- */
.wm-spine {{
    display: flex; align-items: stretch; gap: 6px; margin: 4px 0 16px;
    padding: 10px 12px; border-radius: 16px;
    background: linear-gradient(180deg, rgba(244,239,228,0.9), rgba(236,229,214,0.9));
    border: 1px solid rgba(142,107,63,0.16); box-shadow: 0 10px 24px rgba(72,66,43,0.06);
}}
.wm-spine-step {{
    flex: 1; text-align: center; padding: 8px 6px; border-radius: 12px;
    font-size: .74rem; font-weight: 700; letter-spacing: .04em; text-transform: uppercase;
    color: #7c7666; background: rgba(255,255,255,0.35); position: relative;
    transition: all .4s ease;
}}
.wm-spine-step.done {{ color: var(--wm-olive-deep); background: rgba(63,107,60,0.10); }}
.wm-spine-step.active {{
    color: #fff; background: linear-gradient(135deg, var(--wm-olive-deep), var(--wm-olive));
    box-shadow: 0 8px 18px rgba(63,107,60,0.28); animation: wmPulse 2.4s ease-in-out infinite;
}}
.wm-spine-step .ico {{ display:block; font-size: 1.1rem; margin-bottom: 2px; }}
.wm-subtrack {{ display:flex; gap:6px; margin:-8px 0 14px; padding:0 4px; }}
.wm-module {{
    flex:1; font-size:.7rem; font-weight:700; text-align:center; padding:6px 4px;
    border-radius:10px; border:1px dashed rgba(142,107,63,0.3); color:#8a7d63;
    background:rgba(255,255,255,0.3); transition: all .4s ease;
}}
.wm-module.s-green {{
    color:#fff; border-style:solid; animation: wmSnap .5s ease both;
    background:linear-gradient(135deg,var(--wm-olive-deep),var(--wm-olive));
}}
.wm-module.s-yellow {{
    color:#6a5320; background:#f3e6cc;
    border-color:var(--wm-paper); border-style:solid;
}}
.wm-module.s-red {{ color:#fff; background:var(--wm-danger); border-style:solid; }}
.wm-module.s-active {{
    color:#fff; border-style:solid; animation: wmPulse 2s ease-in-out infinite;
    background:linear-gradient(135deg,#4a5042,#5e7d4f);
}}

/* --- Avatar roster + satisfaction meters --- */
.wm-roster {{ display:flex; flex-wrap:wrap; gap:10px; margin:6px 0 14px; }}
.wm-av-card {{
    flex:1 1 150px; min-width:140px; border-radius:16px; padding:10px;
    background:rgba(247,243,232,0.9); border:1px solid rgba(142,107,63,0.15);
    box-shadow:0 10px 22px rgba(72,66,43,0.06); text-align:center;
    transition: transform .25s ease, box-shadow .25s ease;
}}
.wm-av-card.speaking {{ transform: translateY(-4px) scale(1.02); box-shadow:0 16px 30px rgba(63,107,60,0.22); }}
.wm-av-name {{ font-weight:700; font-size:.86rem; margin-top:4px; }}
.wm-av-title {{ font-size:.7rem; color:#7c7666; }}
.wm-meter {{ height:8px; border-radius:999px; background:rgba(142,107,63,0.16); margin-top:7px; overflow:hidden; }}
.wm-meter > span {{
    display:block; height:100%; border-radius:999px;
    background:linear-gradient(90deg,var(--wm-olive),var(--wm-olive-deep));
    transition: width 1.1s cubic-bezier(.22,1,.36,1);
}}
.wm-meter.low > span {{ background:linear-gradient(90deg,#d8a25a,var(--wm-danger)); }}

/* --- City banner --- */
.wm-city {{
    border-radius:18px; overflow:hidden; margin-bottom:14px;
    border:1px solid rgba(142,107,63,0.18); box-shadow:0 14px 30px rgba(72,66,43,0.10);
}}
.wm-city svg {{ display:block; width:100%; height:auto; }}
.wm-city-cap {{
    font-size:.78rem; padding:6px 12px; color:#5b4a32;
    background:rgba(244,239,228,0.92); border-top:1px solid rgba(142,107,63,0.14);
}}

/* --- Vote tally board --- */
.wm-vote-row {{
    display:flex; align-items:center; gap:10px; padding:8px 12px; margin-bottom:8px;
    border-radius:14px; background:rgba(247,243,232,0.9); border:1px solid rgba(142,107,63,0.14);
    animation: wmVoteIn .5s ease both;
}}
.wm-pill {{ font-size:.72rem; font-weight:700; padding:3px 10px; border-radius:999px; color:#fff; }}
.wm-pill.v-green {{ background:var(--wm-olive-deep); }}
.wm-pill.v-yellow {{ background:var(--wm-paper); color:#5b4a32; }}
.wm-pill.v-neutral {{ background:var(--wm-sage); }}
.wm-pill.v-red {{ background:var(--wm-danger); }}

/* --- Earned badges --- */
.wm-badge-trophy {{
    display:inline-flex; align-items:center; gap:8px; padding:8px 14px; margin:0 8px 8px 0;
    border-radius:14px; font-weight:700; font-size:.84rem; color:#5b4a32;
    background:linear-gradient(180deg,#f6edd6,#ecdcbb); border:1px solid rgba(142,107,63,0.25);
    box-shadow:0 8px 18px rgba(72,66,43,0.10); animation: wmSnap .6s ease both;
}}

/* --- SWM hero logo (on setup screen) --- */
.cx-setup-hero {{ text-align: center; padding: 28px 0 16px; position: relative; }}
.cx-setup-hero img.logo {{
    width: 100%; max-width: 420px; height: auto; display: block; margin: 0 auto;
    filter: drop-shadow(0 6px 14px rgba(72, 66, 43, 0.08));
    animation: cxLogoIn 0.8s cubic-bezier(.22,1,.36,1) both;
}}

/* --- Keyframes --- */
@keyframes wmFadeIn {{ from {{ opacity:0; transform:translateY(6px); }} to {{ opacity:1; transform:none; }} }}
@keyframes wmSnap {{
    0% {{ opacity:0; transform:scale(.94); }}
    60% {{ transform:scale(1.03); }}
    100% {{ opacity:1; transform:scale(1); }}
}}
@keyframes wmShake {{
    0%,100% {{ transform:translateX(0); }}
    20% {{ transform:translateX(-5px); }} 40% {{ transform:translateX(5px); }}
    60% {{ transform:translateX(-3px); }} 80% {{ transform:translateX(3px); }}
}}
@keyframes wmPulse {{
    0%,100% {{ box-shadow:0 8px 18px rgba(63,107,60,0.28); }}
    50% {{ box-shadow:0 8px 26px rgba(63,107,60,0.45); }}
}}
@keyframes wmVoteIn {{ from {{ opacity:0; transform:translateX(-14px); }} to {{ opacity:1; transform:none; }} }}
@keyframes wmTypingDot {{
    0%, 60%, 100% {{ transform: translateY(0)   scale(.85); opacity: .35; }}
    30%           {{ transform: translateY(-4px) scale(1);   opacity: 1; }}
}}
@keyframes wmSpeakDot {{
    0%, 100% {{ transform: scale(1);   opacity: .4; }}
    50%      {{ transform: scale(1.5); opacity: .95; }}
}}
@keyframes cxAurora {{
    0%   {{ transform: translate(0, 0) scale(1);    opacity: 0.85; }}
    50%  {{ transform: translate(-3%, 2%) scale(1.06); opacity: 1; }}
    100% {{ transform: translate(2%, -3%) scale(0.98); opacity: 0.85; }}
}}
@keyframes cxLogoIn {{
    0%   {{ opacity: 0; transform: translateY(8px) scale(0.97); }}
    100% {{ opacity: 1; transform: translateY(0)   scale(1); }}
}}
@keyframes cxDot {{
    0%   {{ box-shadow: 0 0 0 0   rgba(63,107,60,0.55); }}
    70%  {{ box-shadow: 0 0 0 8px rgba(63,107,60,0); }}
    100% {{ box-shadow: 0 0 0 0   rgba(63,107,60,0); }}
}}
{effects_css}

/* =============================================================
   UI POLISH PACK — micro-interactions, focus rings, refined
   hierarchy. Layered last so it wins specificity tussles.
   ============================================================= */

/* --- Chrome bar: subtler, less heavy at the top of every screen --- */
.cx-chrome {{
    padding: 8px 16px !important;
    background: linear-gradient(180deg, rgba(247,243,232,0.92), rgba(247,243,232,0.72)) !important;
    border: 1px solid rgba(94,125,79,0.20) !important;
    border-radius: 999px !important;
    backdrop-filter: blur(4px);
    margin-bottom: 6px;
}}
.cx-chrome-logo .wordmark {{ font-size: 20px !important; }}
.cx-chrome-logo .tag {{ opacity: 0.78; font-size: 11px; letter-spacing: 0.08em; }}
.cx-chip {{
    background: rgba(63,107,60,0.10) !important;
    color: var(--wm-olive-deep) !important;
    border: 1px solid rgba(63,107,60,0.22) !important;
    padding: 4px 12px !important; border-radius: 999px !important;
    font-weight: 700; letter-spacing: 0.06em;
}}
.cx-chip .dot {{
    width: 8px; height: 8px; border-radius: 50%;
    background: var(--wm-olive-deep); display: inline-block; margin-right: 6px;
    animation: cxDot 1.8s ease-out infinite;
}}

/* --- Round header: stronger hierarchy, gentle inner shimmer --- */
.round-hdr {{
    padding: 18px 22px !important;
    border-radius: 22px !important;
    box-shadow: 0 22px 40px rgba(28,64,46,0.22), inset 0 1px 0 rgba(255,255,255,0.10);
    background:
        linear-gradient(135deg, rgba(74,80,66,0.98) 0%, rgba(94,125,79,0.98) 54%, rgba(126,145,101,0.98) 100%),
        radial-gradient(circle at 90% -10%, rgba(255,255,255,0.12), transparent 45%);
    background-blend-mode: lighten;
    animation: wmFadeIn .4s ease both;
}}
.round-hdr h3 {{ font-size: 1.55rem !important; line-height: 1.15 !important; letter-spacing: -0.005em; }}
.round-hdr p  {{ opacity: 0.92; margin-top: 4px; }}

/* --- Spine: tighter sub-track, clearer "you are here" --- */
.wm-spine-step {{
    transition: transform .25s ease, box-shadow .25s ease, background .25s ease;
}}
.wm-spine-step.active {{ transform: translateY(-1px); }}
.wm-subtrack {{ margin: 4px 0 14px !important; gap: 8px; }}
.wm-module {{
    padding: 7px 10px !important;
    font-size: .72rem !important;
    transition: transform .25s ease, box-shadow .25s ease;
}}
.wm-module.s-active {{ transform: scale(1.03); }}

/* --- Proposal boxes: subtle hover lift to feel alive --- */
.proposal-box {{
    transition: transform .18s ease, box-shadow .18s ease, border-color .25s ease;
}}
.proposal-box:hover {{
    transform: translateY(-1px);
    box-shadow: 0 18px 36px rgba(72,66,43,0.10);
}}

/* --- Transcript bubbles: gentle hover --- */
.msg-bubble {{ transition: transform .18s ease, box-shadow .18s ease; }}
.msg-bubble:hover {{
    transform: translateY(-1px);
    box-shadow: 0 14px 30px rgba(72,66,43,0.10);
}}

/* --- Vote rows: lift on hover to look interactive --- */
.wm-vote-row {{ transition: transform .18s ease, box-shadow .18s ease; }}
.wm-vote-row:hover {{
    transform: translateX(2px);
    box-shadow: 0 12px 24px rgba(72,66,43,0.10);
}}

/* --- Avatar cards: smoother speaking glow + no name truncation --- */
.wm-av-card {{
    transition: transform .25s cubic-bezier(.22,1,.36,1),
                box-shadow .25s ease, border-color .25s ease;
}}
.wm-av-card.speaking {{
    transform: translateY(-6px) scale(1.03);
    box-shadow: 0 22px 36px rgba(63,107,60,0.32);
    border-color: var(--wm-olive-deep);
}}
.wm-av-name {{
    white-space: normal !important;
    overflow: visible !important;
    text-overflow: clip !important;
    line-height: 1.2;
}}
.wm-av-title {{
    white-space: normal;
    line-height: 1.2;
    margin-top: 2px;
}}

/* --- Form widgets: olive focus ring, clearer labels --- */
[data-testid="stTextArea"] textarea:focus,
[data-testid="stTextInput"] input:focus {{
    outline: none !important;
    border-color: var(--wm-olive-deep) !important;
    box-shadow: 0 0 0 3px rgba(63,107,60,0.18) !important;
}}
[data-testid="stTextArea"] label,
[data-testid="stTextInput"] label,
[data-testid="stSelectbox"] label,
[data-testid="stMultiSelect"] label,
[data-testid="stRadio"] label {{
    font-weight: 600 !important;
    color: var(--wm-charcoal) !important;
}}

/* --- Primary button: a touch more confident --- */
[data-testid="stButton"] button[kind="primary"] {{
    padding: 10px 22px !important;
    font-size: 1rem !important;
    letter-spacing: 0.01em;
    box-shadow: 0 14px 30px rgba(63,107,60,0.28) !important;
}}
[data-testid="stButton"] button[kind="primary"]:hover {{
    transform: translateY(-1px);
    box-shadow: 0 18px 36px rgba(63,107,60,0.36) !important;
}}

/* --- Sidebar: structured dossier --- */
.wm-dossier {{
    padding: 12px 14px;
    border-radius: 14px;
    background: rgba(247,243,232,0.85);
    border: 1px solid rgba(94,125,79,0.18);
    box-shadow: 0 8px 18px rgba(72,66,43,0.06);
    margin-bottom: 12px;
    position: relative;
    overflow: hidden;
}}
.wm-dossier::before {{
    content: ""; position: absolute; left: 0; top: 0; bottom: 0; width: 4px;
    background: var(--accent, var(--wm-olive-deep));
}}
.wm-dossier h4 {{
    margin: 0 0 6px !important;
    font-size: 0.72rem !important;
    text-transform: uppercase;
    letter-spacing: 0.10em;
    color: var(--wm-olive-deep);
    font-weight: 800 !important;
}}
.wm-dossier ul {{ margin: 4px 0 0; padding-left: 18px; }}
.wm-dossier li {{ margin-bottom: 4px; font-size: 0.86rem; line-height: 1.35; }}

/* --- Outcome verdict: bigger, animated --- */
.wm-verdict {{
    text-align: center;
    padding: 26px 16px 14px;
    border-radius: 20px;
    background: linear-gradient(180deg, rgba(247,243,232,0.92), rgba(247,243,232,0.68));
    border: 1px solid rgba(94,125,79,0.25);
    box-shadow: 0 22px 40px rgba(72,66,43,0.14);
    margin: 6px 0 14px;
    animation: wmFadeIn .5s ease both, cxRibbon .8s ease both;
}}
.wm-verdict .title {{
    font-family: var(--wm-font-display);
    font-size: 2.6rem; font-weight: 700; line-height: 1.05;
    letter-spacing: -0.01em;
    margin-bottom: 6px;
}}
.wm-verdict.pass .title {{ color: var(--wm-olive-deep); }}
.wm-verdict.partial .title {{ color: var(--wm-paper); }}
.wm-verdict.fail .title {{ color: var(--wm-danger); }}
.wm-verdict .subtitle {{
    font-size: 1.0rem; color: var(--fg-2, #5b4a32);
    max-width: 740px; margin: 0 auto;
}}
.wm-verdict .meter {{
    display: inline-block; margin-top: 12px; padding: 5px 14px;
    border-radius: 999px; background: rgba(63,107,60,0.10);
    color: var(--wm-olive-deep); font-weight: 700;
    border: 1px solid rgba(63,107,60,0.22);
}}
@keyframes cxRibbon {{
    0%   {{ clip-path: inset(0 50% 0 50%); opacity: 0; }}
    20%  {{ opacity: 1; }}
    100% {{ clip-path: inset(0 0 0 0); opacity: 1; }}
}}

/* --- Earned-badge chips: more presence --- */
.wm-badge-trophy {{
    font-size: 0.92rem !important;
    padding: 9px 16px !important;
    box-shadow: 0 10px 22px rgba(72,66,43,0.14) !important;
}}

/* --- Kill Streamlit's bottom chrome (footer, "Made with…", status, deploy)
       and the leftover conveyor band that was reading as a permanent bar --- */
footer {{ visibility: hidden !important; height: 0 !important; }}
[data-testid="stStatusWidget"] {{ display: none !important; }}
[data-testid="stDecoration"] {{ display: none !important; }}
.stDeployButton, [data-testid="stDeployButton"],
[data-testid="stToolbarActions"] {{ display: none !important; }}
.cx-bg-conveyor {{ display: none !important; }}

/* --- Universal button theming: every button variant Streamlit ships
       inherits the same olive-primary / cream-secondary look. --- */
[data-testid="stButton"] button,
[data-testid="stFormSubmitButton"] button,
[data-testid="stDownloadButton"] button,
[data-testid="stLinkButton"] a,
[data-testid="baseButton-secondary"],
[data-testid="baseButton-primary"] {{
    border-radius: 999px !important;
    border: 1px solid rgba(94,125,79,0.20) !important;
    background: linear-gradient(180deg, #f5efe2 0%, #eadfcb 100%) !important;
    color: #4c402a !important;
    font-weight: 600 !important;
    box-shadow: 0 8px 20px rgba(72,66,43,0.08);
    transition: transform .15s ease, box-shadow .15s ease, filter .15s ease;
}}
[data-testid="stButton"] button:hover,
[data-testid="stFormSubmitButton"] button:hover,
[data-testid="stDownloadButton"] button:hover,
[data-testid="stLinkButton"] a:hover {{
    transform: translateY(-1px);
    filter: brightness(1.02);
    box-shadow: 0 12px 26px rgba(72,66,43,0.12);
}}
/* Primary variants — olive gradient with white text. */
[data-testid="stButton"] button[kind="primary"],
[data-testid="stFormSubmitButton"] button[kind="primary"],
[data-testid="baseButton-primary"] {{
    background: linear-gradient(135deg, var(--wm-olive-deep) 0%, var(--wm-olive) 100%) !important;
    color: #ffffff !important;
    border-color: var(--wm-olive-deep) !important;
    box-shadow: 0 14px 30px rgba(63,107,60,0.28) !important;
}}
[data-testid="stButton"] button[kind="primary"]:hover,
[data-testid="stFormSubmitButton"] button[kind="primary"]:hover,
[data-testid="baseButton-primary"]:hover {{
    color: #ffffff !important;
}}
/* Download button — primary look (was unreadable before). */
[data-testid="stDownloadButton"] button {{
    background: linear-gradient(135deg, var(--wm-olive-deep) 0%, var(--wm-olive) 100%) !important;
    color: #ffffff !important;
    border-color: var(--wm-olive-deep) !important;
    box-shadow: 0 12px 26px rgba(63,107,60,0.24);
}}
[data-testid="stDownloadButton"] button:hover {{ color: #ffffff !important; }}

/* --- Radios: themed unchecked + checked + label hover --- */
[data-baseweb="radio"] div[role="radio"] {{
    border: 2px solid rgba(94,125,79,0.45) !important;
    background: rgba(247,243,232,0.85) !important;
}}
[data-baseweb="radio"] div[role="radio"][aria-checked="true"] {{
    background: var(--wm-olive-deep) !important;
    border-color: var(--wm-olive-deep) !important;
    box-shadow: 0 0 0 4px rgba(63,107,60,0.18) !important;
}}
[data-baseweb="radio"] div[role="radio"][aria-checked="true"]::after {{
    background: #ffffff !important;
}}
[data-testid="stRadio"] label:hover {{ color: var(--wm-olive-deep) !important; }}

/* --- Checkboxes: themed --- */
[data-baseweb="checkbox"] div[role="checkbox"] {{
    border-color: rgba(94,125,79,0.45) !important;
    background: rgba(247,243,232,0.85) !important;
}}
[data-baseweb="checkbox"] div[role="checkbox"][aria-checked="true"] {{
    background: var(--wm-olive-deep) !important;
    border-color: var(--wm-olive-deep) !important;
}}
[data-baseweb="checkbox"] label,
[data-testid="stCheckbox"] label,
[data-testid="stCheckbox"] label p {{
    color: var(--wm-charcoal) !important;
    -webkit-text-fill-color: var(--wm-charcoal) !important;
    opacity: 1 !important;
}}

/* =============================================================
   PORTALED DROPDOWN LIST — Streamlit portals the open popover
   outside .block-container, so we need top-level !important
   selectors to repaint it cream-paper instead of black.
   ============================================================= */
div[data-baseweb="popover"],
div[data-baseweb="popover"] > div,
div[data-baseweb="popover"] [data-baseweb="menu"],
ul[role="listbox"],
div[role="listbox"] {{
    background: rgba(247, 243, 232, 0.98) !important;
    color: var(--wm-charcoal) !important;
    border: 1px solid rgba(94,125,79,0.30) !important;
    border-radius: 12px !important;
    box-shadow: 0 16px 32px rgba(72,66,43,0.18) !important;
    backdrop-filter: blur(2px);
}}
/* Reset every inner element's colour scheme — Streamlit/BaseWeb sometimes
   inherits dark-mode classes for the portal. */
div[data-baseweb="popover"] *,
[data-baseweb="menu"] *,
ul[role="listbox"] *,
div[role="listbox"] * {{
    color: var(--wm-charcoal) !important;
    -webkit-text-fill-color: var(--wm-charcoal) !important;
}}
/* The list items themselves — transparent base, olive on hover/selected. */
[data-baseweb="popover"] li,
[data-baseweb="popover"] [role="option"],
[role="listbox"] li,
[role="listbox"] [role="option"],
[data-baseweb="menu"] li {{
    background: transparent !important;
    color: var(--wm-charcoal) !important;
    border-radius: 8px !important;
    margin: 2px 4px !important;
    padding: 8px 10px !important;
}}
[data-baseweb="popover"] li:hover,
[data-baseweb="popover"] [role="option"]:hover,
[data-baseweb="popover"] [role="option"][aria-selected="true"],
[data-baseweb="popover"] [role="option"][aria-checked="true"],
[role="listbox"] li:hover,
[role="listbox"] [role="option"]:hover,
[role="listbox"] [role="option"][aria-selected="true"],
[data-baseweb="menu"] li:hover {{
    background: rgba(94,125,79,0.18) !important;
    color: var(--wm-olive-deep) !important;
}}
[data-baseweb="popover"] li:hover *,
[data-baseweb="popover"] [role="option"]:hover *,
[data-baseweb="popover"] [role="option"][aria-selected="true"] *,
[role="listbox"] [role="option"]:hover *,
[role="listbox"] [role="option"][aria-selected="true"] * {{
    color: var(--wm-olive-deep) !important;
    -webkit-text-fill-color: var(--wm-olive-deep) !important;
}}

/* =============================================================
   FORCED THEMING — popover trigger + selectbox + multiselect.
   Streamlit ships several DOM variants across minor versions;
   this block targets all of them with high specificity.
   ============================================================= */

/* "What do I do here?" popover trigger — every Streamlit variant. */
[data-testid="stPopover"] > div > button,
[data-testid="stPopover"] button,
[data-testid="stPopoverButton"],
button[data-testid="stPopoverButton"],
[data-testid="stPopover"] [data-testid^="stBaseButton"] {{
    background: linear-gradient(180deg, rgba(247,243,232,0.96) 0%, rgba(238,228,206,0.96) 100%) !important;
    color: var(--wm-olive-deep) !important;
    border: 1px solid rgba(94,125,79,0.32) !important;
    border-radius: 999px !important;
    font-weight: 700 !important;
    box-shadow: 0 8px 18px rgba(72,66,43,0.08) !important;
}}
[data-testid="stPopover"] > div > button:hover,
[data-testid="stPopover"] button:hover,
[data-testid="stPopoverButton"]:hover {{
    background: linear-gradient(180deg, #f0e6cb 0%, #e6d8b6 100%) !important;
    color: var(--wm-olive-deep) !important;
}}
/* Popover body (the panel that opens). */
[data-testid="stPopoverBody"],
[data-baseweb="popover"] div[data-testid="stPopoverBody"],
[data-baseweb="popover"] [role="dialog"] {{
    background: rgba(247,243,232,0.98) !important;
    color: var(--wm-charcoal) !important;
    border: 1px solid rgba(94,125,79,0.30) !important;
    border-radius: 14px !important;
    box-shadow: 0 18px 36px rgba(72,66,43,0.18) !important;
}}

/* Selectbox CLOSED control — role/model/currency pickers.
   Use cream paper instead of a dark button; the final normalization block
   below removes BaseWeb's nested dark-mode fragments. */
[data-testid="stSelectbox"] [data-baseweb="select"],
[data-testid="stSelectbox"] [data-baseweb="select"] > div,
[data-testid="stSelectbox"] [data-baseweb="select"] > div > div,
[data-testid="stSelectbox"] [data-baseweb="select"] [role="combobox"] {{
    background: rgba(247,243,232,0.96) !important;
    border-color: rgba(94,125,79,0.42) !important;
    border-radius: 12px !important;
}}
[data-testid="stSelectbox"] [data-baseweb="select"] *,
[data-testid="stSelectbox"] [data-baseweb="select"] svg {{
    color: var(--wm-charcoal) !important;
    -webkit-text-fill-color: var(--wm-charcoal) !important;
    fill: var(--wm-olive-deep) !important;
}}

/* Multiselect CLOSED control — priority dimensions picker. Cream paper
   with olive border and olive chips. */
[data-testid="stMultiSelect"] [data-baseweb="select"],
[data-testid="stMultiSelect"] [data-baseweb="select"] > div,
[data-testid="stMultiSelect"] [data-baseweb="select"] > div > div {{
    background: rgba(247,243,232,0.95) !important;
    border: 1px solid rgba(94,125,79,0.40) !important;
    border-radius: 12px !important;
    box-shadow: 0 6px 14px rgba(72,66,43,0.06) !important;
}}
[data-testid="stMultiSelect"] [data-baseweb="select"] [role="combobox"] {{
    background: transparent !important;
    color: var(--wm-charcoal) !important;
}}
/* Selected priority chips (olive pills with white text + remove ×). */
[data-testid="stMultiSelect"] [data-baseweb="tag"] {{
    background: var(--wm-olive-deep) !important;
    color: #ffffff !important;
    border-radius: 999px !important;
    padding: 2px 4px !important;
    border: 1px solid var(--wm-olive-deep) !important;
}}
[data-testid="stMultiSelect"] [data-baseweb="tag"] *,
[data-testid="stMultiSelect"] [data-baseweb="tag"] svg {{
    color: #ffffff !important;
    fill: #ffffff !important;
}}
[data-testid="stMultiSelect"] [data-baseweb="tag"]:hover {{
    background: var(--wm-olive) !important;
    filter: brightness(1.05);
}}
/* Multiselect dropdown caret / placeholder colour. */
[data-testid="stMultiSelect"] [data-baseweb="select"] svg {{
    color: var(--wm-olive-deep) !important;
    fill: var(--wm-olive-deep) !important;
}}

/* =============================================================
   FINAL SELECT / DROPDOWN NORMALIZATION
   BaseWeb changes its internal div structure across Streamlit versions.
   Earlier broad rules can accidentally paint nested value containers black or
   create a visible "box inside a box". This final pass styles only the real
   control surface and lets inner layout divs stay transparent.
   ============================================================= */
[data-testid="stSelectbox"] [data-baseweb="select"],
[data-testid="stMultiSelect"] [data-baseweb="select"] {{
    background: rgba(247,243,232,0.96) !important;
    border: 1px solid rgba(94,125,79,0.42) !important;
    border-radius: 14px !important;
    box-shadow: 0 8px 18px rgba(72,66,43,0.07) !important;
    min-height: 44px !important;
    overflow: hidden !important;
}}
[data-testid="stSelectbox"] [data-baseweb="select"] > div,
[data-testid="stSelectbox"] [data-baseweb="select"] > div > div,
[data-testid="stSelectbox"] [data-baseweb="select"] [role="combobox"],
[data-testid="stMultiSelect"] [data-baseweb="select"] > div,
[data-testid="stMultiSelect"] [data-baseweb="select"] > div > div,
[data-testid="stMultiSelect"] [data-baseweb="select"] [role="combobox"] {{
    background: transparent !important;
    border: 0 !important;
    box-shadow: none !important;
    min-height: 42px !important;
}}
[data-testid="stSelectbox"] [data-baseweb="select"] [role="combobox"],
[data-testid="stMultiSelect"] [data-baseweb="select"] [role="combobox"] {{
    padding: 0 12px !important;
    display: flex !important;
    align-items: center !important;
}}
[data-testid="stSelectbox"] [data-baseweb="select"] *,
[data-testid="stMultiSelect"] [data-baseweb="select"] input,
[data-testid="stMultiSelect"] [data-baseweb="select"] span {{
    color: var(--wm-charcoal) !important;
    -webkit-text-fill-color: var(--wm-charcoal) !important;
}}
[data-testid="stSelectbox"] [data-baseweb="select"] svg,
[data-testid="stMultiSelect"] [data-baseweb="select"] svg {{
    color: var(--wm-olive-deep) !important;
    fill: var(--wm-olive-deep) !important;
}}

/* Portal shells should be invisible; only the actual menu/listbox gets the
   cream paper surface. This fixes the strange oversized padding box. */
div[data-baseweb="popover"],
div[data-baseweb="popover"] > div {{
    background: transparent !important;
    border: 0 !important;
    box-shadow: none !important;
    padding: 0 !important;
}}
div[data-baseweb="popover"] [data-baseweb="menu"],
div[data-baseweb="popover"] [role="listbox"],
ul[role="listbox"],
div[role="listbox"] {{
    background: rgba(247,243,232,0.99) !important;
    border: 1px solid rgba(94,125,79,0.34) !important;
    border-radius: 14px !important;
    box-shadow: 0 18px 36px rgba(72,66,43,0.18) !important;
    color: var(--wm-charcoal) !important;
    padding: 6px !important;
    overflow: hidden !important;
}}
/* Streamlit's virtualized select menu may omit role="listbox" on its scroll
   containers. Repaint every popover descendant cream, but do not add borders
   or padding to descendants; otherwise the dropdown becomes a box-within-box. */
div[data-baseweb="popover"] div:not([data-testid="stPopoverBody"]) {{
    background-color: rgba(247,243,232,0.99) !important;
    color: var(--wm-charcoal) !important;
    border-color: transparent !important;
    box-shadow: none !important;
}}
div[data-baseweb="popover"] [role="option"],
div[data-baseweb="popover"] li,
ul[role="listbox"] [role="option"],
div[role="listbox"] [role="option"] {{
    min-height: 36px !important;
    display: flex !important;
    align-items: center !important;
    background: rgba(247,243,232,0.99) !important;
    color: var(--wm-charcoal) !important;
    -webkit-text-fill-color: var(--wm-charcoal) !important;
    border-radius: 10px !important;
    margin: 1px 0 !important;
    padding: 8px 12px !important;
}}
div[data-baseweb="popover"] [role="option"]:hover,
div[data-baseweb="popover"] [role="option"][aria-selected="true"],
div[data-baseweb="popover"] [role="option"][aria-checked="true"],
ul[role="listbox"] [role="option"]:hover,
ul[role="listbox"] [role="option"][aria-selected="true"],
div[role="listbox"] [role="option"]:hover,
div[role="listbox"] [role="option"][aria-selected="true"] {{
    background: rgba(94,125,79,0.18) !important;
    color: var(--wm-olive-deep) !important;
    -webkit-text-fill-color: var(--wm-olive-deep) !important;
}}

</style>
"""
