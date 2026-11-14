#!/usr/bin/env python3
"""Repair incorrectly generated crest markup on league season final tables."""
from pathlib import Path
import re
root=Path(__file__).resolve().parents[1]/'competitions'
prefixes=('alpha-league','beta-league','gamma-league','mainland-league','islands-league','mainland-first-division','islands-first-division')
fixed_pages=0
fixed_rows=0
for page in sorted(root.glob('*.html')):
    if not any(re.fullmatch(re.escape(p)+r'-\d{4}-\d{2}\.html',page.name) for p in prefixes):continue
    s=page.read_text(encoding='utf-8')
    # Previous rollout accidentally interpolated href into an img attribute,
    # and lost the opening <a> tag. Restore the original link and proper image.
    pattern=r'<img class="league-club-crest" src="\.\./clubs/crests/([^"]+?)\.html">\.png" alt="" aria-hidden="true" loading="lazy"/>((?:\.\./clubs/)(?:[^"<]+?)/?[^"<]*?\.html)([^<]+)</a>'
    def repair(m):
        slug=m.group(1)
        href=m.group(2)
        label=m.group(3)
        return f'<img class="league-club-crest" src="../clubs/crests/{slug}.png" alt="" aria-hidden="true" loading="lazy"/><a href="{href}">{label}</a>'
    updated,n=re.subn(pattern,repair,s)
    if n:
        page.write_text(updated,encoding='utf-8')
        fixed_pages+=1
        fixed_rows+=n
print(f'Repaired {fixed_rows} club rows on {fixed_pages} league-season pages')
