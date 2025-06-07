#!/usr/bin/env python3
import os, html

for dirpath, dirnames, filenames in os.walk("."):
    with open(os.path.join(dirpath, "index.html"), "w", encoding="utf-8") as f:
        rel = os.path.relpath(dirpath, ".")
        title = "/" if rel == "." else rel
        f.write(f"<!DOCTYPE html><html lang='en'><head><meta charset='utf-8'>"
                f"<title>Index of {title}</title></head><body><h1>Index of {title}</h1><ul>")
        for name in sorted(dirnames + filenames):
            if name == "index.html": continue
            link = html.escape(name)
            slash = "/" if name in dirnames else ""
            href = f"{link}/index.html" if name in dirnames else link
            f.write(f"<li><a href='{href}'>{link}{slash}</a></li>")
        f.write("</ul></body></html>")
