#!/usr/bin/env python3
"""Convert an OpenDocument Spreadsheet (.ods) to Markdown.

Dependency-free: reads content.xml from the ODS zip and renders each sheet
as a Markdown section. Cell line breaks become Markdown line breaks.

Usage:
    py scripts/ods_to_md.py [INPUT.ods] [-o OUTPUT.md]

Defaults: INPUT = first .ods in the project root,
          OUTPUT = doc/<ods-filename>.md
"""

import argparse
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

NS = {
    "table": "urn:oasis:names:tc:opendocument:xmlns:table:1.0",
    "text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
}
T = "{%s}" % NS["table"]
TEXT_S = "{%s}s" % NS["text"]
TEXT_TAB = "{%s}tab" % NS["text"]

MAX_REPEAT = 200  # guard against huge repeated empty columns


def cell_text(cell: ET.Element) -> str:
    """Join paragraphs of a cell with markdown line breaks."""
    paras = []
    for p in cell.findall("text:p", NS):
        parts = []
        for node in p.iter():
            if node.tag in (TEXT_S, TEXT_TAB):  # space / tab elements
                parts.append(" ")
                continue
            if node.text:
                parts.append(node.text)
            if node.tail:
                parts.append(node.tail)
        paras.append("".join(parts).strip())

    def esc(t: str) -> str:
        return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    text = "<br>".join(esc(t) for t in paras if t)
    return text.replace("|", "\\|")


def read_rows(table: ET.Element) -> list[list[str]]:
    """Return list of rows, each a list of cell strings, honoring repeats."""
    rows = []
    for row in table.findall(T + "table-row"):
        rrep = int(row.get(T + "number-rows-repeated", "1"))
        cells: list[str] = []
        for cell in row.findall(T + "table-cell"):
            crep = int(cell.get(T + "number-columns-repeated", "1"))
            text = cell_text(cell)
            cells.extend([text] * min(crep, MAX_REPEAT))
        while cells and cells[-1] == "":
            cells.pop()
        for _ in range(min(rrep, MAX_REPEAT)):
            rows.append(list(cells))
        if rrep > MAX_REPEAT:
            break
    while rows and not rows[-1]:
        rows.pop()
    return rows


def slug(text: str) -> str:
    s = re.sub(r"[^\w\s-]", "", text.lower())
    return re.sub(r"[\s_]+", "-", s).strip("-")


def sheet_to_md(name: str, rows: list[list[str]]) -> str:
    out = [f"## Sheet: {name}", ""]
    if not rows:
        out.append("_(empty sheet)_")
        return "\n".join(out)
    width = max(len(r) for r in rows)
    header, body = rows[0], rows[1:]
    header = [h or " " for h in header] + [" "] * (width - len(header))
    out.append("| " + " | ".join(header) + " |")
    out.append("|" + "|".join([" --- "] * width) + "|")
    for row in body:
        row = row + [""] * (width - len(row))
        out.append("| " + " | ".join(c or " " for c in row) + " |")
    return "\n".join(out)


def ods_to_markdown(ods_path: Path) -> str:
    with zipfile.ZipFile(ods_path) as zf:
        root = ET.fromstring(zf.read("content.xml"))
    sections = []
    for table in root.iter(T + "table"):
        name = (table.get(T + "name") or "Sheet").strip()
        rows = read_rows(table)
        sections.append(sheet_to_md(name, rows))
    title = ods_path.stem.strip()
    return f"# {title}\n\n" + "\n\n---\n\n".join(sections) + "\n"


def main() -> int:
    here = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", help="input .ods file")
    parser.add_argument("-o", "--output", help="output .md file")
    args = parser.parse_args()

    src = Path(args.input) if args.input else next(iter(here.glob("*.ods")), None)
    if not src or not src.is_file():
        parser.error("no input .ods found")
    if not args.output:
        out_dir = here / "doc"
        out_dir.mkdir(exist_ok=True)
        args.output = str(out_dir / f"{src.stem.strip()}.md")

    md = ods_to_markdown(src)
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(md, encoding="utf-8")
    print(f"wrote {out_path} ({len(md.splitlines())} lines)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
