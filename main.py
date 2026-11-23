"""Entry point: render the front page and write entry.png.

Standard library only. Output directory comes from MAKEFUN_OUTPUT_DIR
and defaults to /output. Deterministic: the render uses no clock, no
randomness, and fixed data, so two runs write byte-identical files.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import draw_frontpage


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, "entry.png")
    draw_frontpage.build(target)
    print("wrote " + target)


if __name__ == "__main__":
    main()
