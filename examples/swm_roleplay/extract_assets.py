"""Extract clean cityscape + 6 neutral avatars from sprites.py for the report.

Run from this directory:
    python extract_assets.py

Output: report_assets/cityscape_clean.svg
        report_assets/avatar_<role_id>.svg  (6 files)
"""
import re
from pathlib import Path
from ui import sprites

ROLES = [
    "national_government",
    "municipal_government",
    "private_sector_company",
    "ngo_civil_society",
    "community_member",
    "informal_sector_worker",
]

# In sprites.py, state "idle" maps to expression "neutral" via _EXPRESSION.
NEUTRAL_STATE = "idle"

OUT = Path(__file__).parent / "report_assets"
OUT.mkdir(exist_ok=True)


def write(path: Path, svg: str) -> None:
    """Make rsvg-convert happy: strip Streamlit HTML wrapper, ensure SVG
    namespaces, prepend XML declaration."""
    # sprites.city() wraps in <div class="wm-city">...</div><div class="wm-city-cap">...</div>
    # Drop the leading <div ...> and everything after </svg>.
    svg = re.sub(r"^\s*<div[^>]*>", "", svg)
    svg = re.sub(r"(</svg>).*$", r"\1", svg, flags=re.DOTALL)
    # Add SVG XML namespaces if the inline element lacks them.
    if 'xmlns="http://www.w3.org/2000/svg"' not in svg:
        svg = svg.replace(
            "<svg ",
            '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" ',
            1,
        )
    if not svg.lstrip().startswith("<?xml"):
        svg = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n' + svg
    path.write_text(svg, encoding="utf-8")
    print(f"  wrote {path.relative_to(Path(__file__).parent)}  ({len(svg):,} bytes)")


def main() -> None:
    print("Extracting clean cityscape...")
    write(OUT / "cityscape_clean.svg", sprites.city(progress=1.0, ruined=False))

    print("Extracting 6 neutral avatars...")
    for role_id in ROLES:
        # Larger render size so the PDF rasterises crisply; SVG is vector anyway.
        svg = sprites.avatar(role_id, state=NEUTRAL_STATE, size=320)
        write(OUT / f"avatar_{role_id}.svg", svg)

    print(f"\nDone. {len(list(OUT.glob('*.svg')))} SVGs in {OUT}/")


if __name__ == "__main__":
    main()
