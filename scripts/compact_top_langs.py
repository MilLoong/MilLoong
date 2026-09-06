"""Rearrange compact top-langs SVG into more columns so the card is shorter."""

from __future__ import annotations

import re
import sys
from pathlib import Path

COLS = 4
ROW_H = 22
PAD_TOP = 18
BAR_GAP = 16
PAD_BOTTOM = 16
COL_W = 207


def compact(svg: str) -> str:
    items = re.findall(r'<g class="stagger".*?</g>', svg, flags=re.S)
    if not items:
        raise SystemExit("no language items found")

    rows = (len(items) + COLS - 1) // COLS
    height = PAD_TOP + 8 + BAR_GAP + rows * ROW_H + PAD_BOTTOM

    svg = re.sub(r'(<svg\s+width="880"\s+height=")\d+(")', rf"\g<1>{height}\2", svg, count=1)
    svg = re.sub(r'viewBox="0 0 880 \d+"', f'viewBox="0 0 880 {height}"', svg, count=1)
    svg = re.sub(
        r'(data-testid="main-card-body"\s+transform="translate\(0, )\d+(\)")',
        rf"\g<1>{PAD_TOP}\2",
        svg,
        count=1,
    )

    blocks = []
    for i, item in enumerate(items):
        col, row = i % COLS, i // COLS
        blocks.append(
            f'<g transform="translate({col * COL_W}, {row * ROW_H})">\n    {item}\n  </g>'
        )

    labels = '<g transform="translate(0, {0})">\n      {1}\n    </g>'.format(
        BAR_GAP + 8,
        "\n      ".join(blocks),
    )
    last_bar = svg.rfind('data-testid="lang-progress"')
    if last_bar < 0:
        raise SystemExit("no progress bars found")
    start = svg.find("<g transform", last_bar)
    end = svg.find("</svg>", start)
    if start < 0 or end < 0:
        raise SystemExit("failed to locate language label block")
    svg = svg[:start] + labels + "\n  \n    " + svg[end:]
    return svg


def main() -> None:
    paths = [Path(p) for p in sys.argv[1:]]
    if not paths:
        raise SystemExit("usage: compact_top_langs.py <svg>...")
    for path in paths:
        path.write_text(compact(path.read_text(encoding="utf-8")), encoding="utf-8")


if __name__ == "__main__":
    main()
