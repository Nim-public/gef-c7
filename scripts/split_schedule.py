#!/usr/bin/env python3
"""Split doc/GEF-C7-Final-Schedule.md into per-phase folders, one folder+file per week.

Layout produced under doc/:
    Phase-0-Onboarding-Base-Camps/Week-0-Onboarding-Base-Camps/Week-0-Onboarding-Base-Camps.md
    Phase-1-24-Week-Plan/Week-01-*/Week-01-*.md ... Week-16-*/Week-16-*.md, Break-Week/Break-Week.md
    Phase-2-Capstone/Weeks-17-24-Capstone/Weeks-17-24-Capstone.md,
                      Program-Ends-Demo-Day/Program-Ends-Demo-Day.md
    Program-Important-Information.md

Usage:
    py scripts/split_schedule.py [SOURCE.md] [-o OUTPUT_DIR]
"""

import argparse
import re
import sys
from pathlib import Path

HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
PHASE_RE = re.compile(r"^Phase\s+(\d+)\s*[—-]\s*(.+)$")
WEEK_RE = re.compile(r"^Week\s+(\d+)\s*[—-]\s*(.+)$")
TRAILING_PARENS_RE = re.compile(r"\s*\([^)]*\)\s*$")

# Phases whose whole content is a single week-level file (no ### week children)
PHASE_UNIT_OVERRIDES = {
    0: ("Week-0-Onboarding-Base-Camps", "Week 0 — Onboarding & Base Camps"),
    2: ("Weeks-17-24-Capstone", "Weeks 17–24 — Capstone Phase 1 and 2"),
}

# Top-level sections kept in the doc root instead of the last phase folder
ROOT_SECTIONS = {"Program — Important Information"}

# Top-level sections that only exist in the master doc and are not split out
MASTER_ONLY_SECTIONS = {"Table of Contents"}


def slug(text: str) -> str:
    s = text.replace("/", "-")
    s = re.sub(r"[^A-Za-z0-9\s-]", "", s)
    return re.sub(r"[\s_-]+", "-", s).strip("-")


def parse_sections(lines: list[str]):
    """Yield (level, title, content_lines) for each ## section."""
    preamble, sections = True, []
    for line in lines:
        m = HEADING_RE.match(line)
        if m and len(m.group(1)) == 2:
            preamble = False
            sections.append([m.group(2).strip(), []])
        elif not preamble and sections:
            sections[-1][1].append(line)
    return sections


def split_units(section_title: str, body: list[str]):
    """Split a section into units: its ### children, or the section itself."""
    phase = PHASE_RE.match(section_title)
    if not phase or int(phase.group(1)) in PHASE_UNIT_OVERRIDES:
        return [(section_title, 2, body)]
    units, current = [], None
    for line in body:
        m = HEADING_RE.match(line)
        if m and len(m.group(1)) == 3:
            if current:
                units.append(current)
            current = [m.group(2).strip(), 3, []]
        elif current:
            current[2].append(line)
    if current:
        units.append(current)
    return units or [(section_title, 2, body)]


def demote(content: list[str], unit_level: int) -> list[str]:
    """Shift inner headings so the unit title can be the single H1."""
    out = []
    for line in content:
        m = HEADING_RE.match(line)
        if m:
            level = max(2, len(m.group(1)) - unit_level + 1)
            out.append("#" * level + " " + m.group(2))
        else:
            out.append(line)
    return out


def strip_tail(content: list[str]) -> list[str]:
    while content and (not content[-1].strip() or content[-1].strip() == "---"):
        content.pop()
    return content


def main() -> int:
    here = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", nargs="?", default=str(here / "doc" / "GEF-C7-Final-Schedule.md"))
    parser.add_argument("-o", "--output-dir", default=str(here / "doc"))
    args = parser.parse_args()

    src = Path(args.source)
    out_root = Path(args.output_dir)
    if not src.is_file():
        parser.error(f"source not found: {src}")

    sections = parse_sections(src.read_text(encoding="utf-8").splitlines())
    if not sections:
        sys.exit("no ## sections found in source")

    created, last_phase_dir = [], None
    for title, body in sections:
        if title in MASTER_ONLY_SECTIONS:
            continue
        phase = PHASE_RE.match(title)
        if phase:
            num = int(phase.group(1))
            folder = f"Phase-{num}-{slug(re.sub(TRAILING_PARENS_RE, '', phase.group(2)))}"
            target = out_root / folder
            last_phase_dir = target
        elif title in ROOT_SECTIONS or last_phase_dir is None:
            target = out_root
        else:
            target = last_phase_dir

        for unit_title, unit_level, unit_body in split_units(title, body):
            if phase and num in PHASE_UNIT_OVERRIDES and unit_title == title:
                file_stem, file_title = PHASE_UNIT_OVERRIDES[num]
            elif unit_level == 3:
                wm = WEEK_RE.match(unit_title)
                if wm:
                    file_stem = f"Week-{int(wm.group(1)):02d}-{slug(wm.group(2))}"
                else:
                    file_stem = slug(unit_title)
                file_title = unit_title
            else:
                file_stem, file_title = slug(unit_title), unit_title

            if target != out_root:
                unit_dir = target / file_stem
            else:
                unit_dir = target
            unit_dir.mkdir(parents=True, exist_ok=True)
            path = unit_dir / f"{file_stem}.md"

            depth = len(path.relative_to(out_root).parts) - 1
            rel = ("../" * depth) + "GEF-C7-Final-Schedule.md"
            lines = [f"# {file_title}", "", f"> Full schedule: [GEF-C7-Final-Schedule.md]({rel})", ""]
            lines += demote(strip_tail(unit_body), unit_level)
            lines.append("")

            text = re.sub(r"\n{3,}", "\n\n", "\n".join(lines))
            path.write_text(text, encoding="utf-8")
            created.append(path.relative_to(out_root))

    print(f"created {len(created)} files under {out_root}:")
    for p in created:
        print(f"  {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
