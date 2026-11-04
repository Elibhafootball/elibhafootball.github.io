#!/usr/bin/env python3
"""Keep the actual SVG geometry; discard stale duplicate viewbox attributes.

HTML attribute names are case-insensitive, so having both viewBox and viewbox
causes browsers to use the wrong viewport and shrink cup bracket typography.
"""
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1] / "competitions"
changed = []
for file in sorted(root.glob("*.html")):
    source = file.read_text(encoding="utf-8")
    def fix(match):
        tag = match.group(0)
        if 'class="knockout-svg' not in tag:
            return tag
        actual = re.search(r'\sviewBox="[^"]+"', tag)
        if not actual:
            return tag
        return re.sub(r'\sviewbox="[^"]+"', '', tag)
    result = re.sub(r'<svg\b[^>]*>', fix, source)
    if result != source:
        file.write_text(result, encoding="utf-8")
        changed.append(file.name)
print(f"Normalized {len(changed)} competition brackets.")
for name in changed:
    print(name)
