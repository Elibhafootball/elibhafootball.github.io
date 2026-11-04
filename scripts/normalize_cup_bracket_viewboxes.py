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
        # The original generated width and height are the true diagram bounds.
        # Many Masherat cups retained a larger, obsolete viewbox from a previous
        # layout. This scales both text and tie boxes down to illegibility.
        # Preserve the FA Cup's existing formatting as the reference.
        if file.name.startswith("fa-cup-"):
            return tag
        width = re.search(r'\bwidth="([0-9.]+)"', tag)
        height = re.search(r'\bheight="([0-9.]+)"', tag)
        if not width or not height:
            return tag
        tag = re.sub(r'\sview[Bb]ox="[^"]+"', '', tag)
        return tag[:-1] + f' viewBox="0 0 {width.group(1)} {height.group(1)}">'
    result = re.sub(r'<svg\b[^>]*>', fix, source)
    if result != source:
        file.write_text(result, encoding="utf-8")
        changed.append(file.name)
print(f"Normalized {len(changed)} competition brackets.")
for name in changed:
    print(name)
