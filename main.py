"""Entry point: render the front page to $MAKEFUN_OUTPUT_DIR/entry.png.

Standard library only. Deterministic: the same bytes every run.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import draw_frontpage


def main():
    # The grader runs this twice; both runs must write identical bytes.
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, "entry.png")
    draw_frontpage.build(target)


if __name__ == "__main__":
    main()
