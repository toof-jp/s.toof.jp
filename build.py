#!/usr/bin/env python3
"""
build.py – Build helper for Cloudflare Pages

• Generates an `_headers` file that makes every non-HTML asset return
  `Content-Type: text/plain; charset=utf-8`.
• Recursively writes a minimalist directory listing (`index.html`) in
  each folder, skipping `.git/`.

Run:
    python build.py [ROOT]

If ROOT is omitted the current directory is used.
"""

import os
import sys
import html
from pathlib import Path
from datetime import datetime

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

HEADERS_CONTENT = """\
/*
  Content-Type: text/plain; charset=utf-8

/*.html
  ! Content-Type
  Content-Type: text/html; charset=utf-8
"""

SKIP_DIRS = {".git"}          # add "__pycache__", ".venv", … if needed
SKIP_FILES = {"index.html", "_headers"}

# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

def write_headers_file(root: Path) -> None:
    """Create or overwrite the _headers file in ROOT."""
    (root / "_headers").write_text(HEADERS_CONTENT, encoding="utf-8")
    print("· _headers file written")


def generate_index(dirpath: Path, root: Path) -> None:
    """Write index.html for a single directory."""
    rel = os.path.relpath(dirpath, root)
    title = "/" if rel == "." else rel

    # Collect entries (dirs first, then files) and sort them case-insensitively.
    dirs = [d for d in dirpath.iterdir() if d.is_dir() and d.name not in SKIP_DIRS]
    files = [f for f in dirpath.iterdir() if f.is_file() and f.name not in SKIP_FILES]
    entries = sorted(dirs, key=lambda p: p.name.lower()) + \
              sorted(files, key=lambda p: p.name.lower())

    out = dirpath / "index.html"
    with out.open("w", encoding="utf-8") as f:
        f.write(
            "<!DOCTYPE html><html lang='en'>"
            "<head><meta charset='utf-8'>"
            f"<title>Index of {html.escape(title)}</title>"
            "<style>"
            "body{font-family:sans-serif;margin:2rem}"
            "ul{list-style:none;padding:0}"
            "li{margin:.2rem 0}"
            "a{text-decoration:none;color:#0366d6}"
            "</style></head><body>"
            f"<h1>Index of {html.escape(title)}</h1><ul>"
        )

        for p in entries:
            name = html.escape(p.name)
            if p.is_dir():
                f.write(f"<li><a href='{name}/index.html'>{name}/</a></li>")
            else:
                f.write(f"<li><a href='{name}'>{name}</a></li>")

        f.write(
            "</ul>"
            f"<p style='color:#888;font-size:.8rem'>"
            f"Generated {datetime.utcnow():%Y-%m-%d %H:%M UTC}</p>"
            "</body></html>"
        )


def generate_all_indexes(root: Path) -> None:
    """Walk ROOT recursively, skipping SKIP_DIRS, and write index.html files."""
    for dirpath, dirnames, _ in os.walk(root, topdown=True):
        # prune directories we do not want to descend into
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        generate_index(Path(dirpath), root)
    print("· index.html files generated")


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #

def main() -> None:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    if not root.is_dir():
        sys.exit(f"Error: {root} is not a directory")

    write_headers_file(root)
    generate_all_indexes(root)
    print(f"Done – site built at {root}")

if __name__ == "__main__":
    main()
