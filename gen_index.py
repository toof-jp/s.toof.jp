#!/usr/bin/env python3
"""
gen_index.py — Recursively generate index.html files under a given directory,
skipping the entire .git tree.

Usage:
    python gen_index.py [ROOT]

If ROOT is omitted, the current working directory (.) is used.
"""

import os
import sys
import html
from pathlib import Path

# Resolve the root directory to process
root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()

for dirpath, dirnames, filenames in os.walk(root, topdown=True):
    # --- Skip .git entirely -------------------------------------------------
    if ".git" in dirnames:
        dirnames.remove(".git")        # Prevent descending into .git/
    # -----------------------------------------------------------------------

    out_path = Path(dirpath) / "index.html"

    # Build a title based on the path relative to the root
    rel = os.path.relpath(dirpath, root)
    title = "/" if rel == "." else rel

    with out_path.open("w", encoding="utf-8") as f:
        # HTML header
        f.write(
            "<!DOCTYPE html><html lang='en'><head>"
            "<meta charset='utf-8'>"
            f"<title>Index of {html.escape(title)}</title>"
            "</head><body>"
            f"<h1>Index of {html.escape(title)}</h1><ul>"
        )

        # Directories first, then files
        for name in sorted(dirnames) + sorted(filenames):
            if name == "index.html":
                continue
            link_text = html.escape(name)
            if name in dirnames:
                # Link into sub-directory index
                f.write(f"<li><a href='{link_text}/index.html'>{link_text}/</a></li>")
            else:
                # Link to a regular file
                f.write(f"<li><a href='{link_text}'>{link_text}</a></li>")

        # Close HTML document
        f.write("</ul></body></html>")

print(f"Done. Generated index.html files under {root}")
