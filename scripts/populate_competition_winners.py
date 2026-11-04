#!/usr/bin/env python3
"""Add winners panels only when a season page unambiguously identifies its winner."""
from pathlib import Path
import html
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / "competitions"
LEAGUES = ("alpha-league", "beta-league", "gamma-league",
           "mainland-league", "islands-league",
           "mainland-first-division", "islands-first-division")
# Knockout formats are recognised by their actual final bracket, not by name.
EARLY_MASHERAT_CUPS = ("brados-cup", "denton-cup", "gresdon-cup", "warfield-cup")
SKIP = {"competition-winner-panel"}

def winner_from_league(page):
    m = re.search(r'<table\b[^>]*class="[^"]*\bleague-table\b[^"]*"[^>]*>.*?<tbody>(.*?)</tbody>', page, re.S)
    if not m:
        return None
    first = re.search(r'<tr\b[^>]*>(.*?)</tr>', m.group(1), re.S)
    if not first or not re.search(r'<td class="pos">\s*1\s*</td>', first.group(1)):
        return None
    club = re.search(r'<td class="club">\s*<a href="([^"]+)">([^<]+)</a>', first.group(1))
    return (html.unescape(club.group(2)), club.group(1)) if club else None

def winner_from_bracket(page):
    # Final tie is the rightmost SVG tie-card; never use earlier round winners.
    cards = re.findall(r'<g class="tie-card">(.*?)</g>', page, re.S)
    candidates = []
    for card in cards:
        box = re.search(r'<rect class="tie-box"[^>]*\bx="([\d.]+)"', card)
        win = re.search(r'<a href="([^"]+)"><text class="[^"]*\bteam\b[^"]*\bwinner\b[^"]*"[^>]*>([^<]+)</text></a>', card)
        if box and win:
            candidates.append((float(box.group(1)), re.sub(r"\s*\(p\)\s*$", "", html.unescape(win.group(2)), flags=re.I), win.group(1)))
    if not candidates:
        return None
    farthest = max(x for x, _, _ in candidates)
    final = [(name, href) for x, name, href in candidates if x == farthest]
    return final[0] if len(final) == 1 else None

def winner_from_single_final(page):
    # Only straightforward one-match finals, no replays or aggregate ties.
    blocks = re.findall(r'<div class="round-block">(.*?)(?=<div class="round-block">|</main>)', page, re.S)
    finals = [b for b in blocks if re.search(r'<h[23]>Final</h[23]>', b)]
    if len(finals) != 1:
        return None
    rows = re.findall(r'<tr>(.*?)</tr>', finals[0], re.S)
    if len(rows) != 1:
        return None
    cells = re.findall(r'<td[^>]*>(.*?)</td>', rows[0], re.S)
    if len(cells) != 3:
        return None
    score = re.fullmatch(r'\s*(\d+)\s*[–-]\s*(\d+)\s*', re.sub(r'<[^>]+>', '', cells[1]))
    if not score or score.group(1) == score.group(2):
        return None
    side = cells[0] if int(score.group(1)) > int(score.group(2)) else cells[2]
    club = re.search(r'<a href="([^"]+)">([^<]+)</a>', side)
    return (html.unescape(club.group(2)), club.group(1)) if club else None

def make_panel(name, href, label):
    slug = href.split("/")[-1].removesuffix(".html")
    if not re.fullmatch(r"[a-z0-9-]+", slug):
        return None
    crest = ROOT / "clubs" / "crests" / (slug + ".png")
    # Missing crest: show the name without a broken-image icon.
    image = (f'<img class="competition-winner-crest" src="../clubs/crests/{slug}.png" '
             f'alt="{html.escape(name, quote=True)} crest">' if crest.exists() else "")
    return ('<section class="competition-winner-panel">' + image +
            '<div><div class="competition-winner-label">' + html.escape(label) +
            '</div><a class="competition-winner-name" href="../clubs/' + slug +
            '.html">' + html.escape(name) + '</a></div></section>')

changed = []
skipped = []
for path in sorted(DIR.glob("*.html")):
    if not re.search(r"-\d{4}-\d{2}\.html$", path.name):
        continue
    page = path.read_text(encoding="utf-8")
    if "competition-winner-panel" in page:
        continue
    slug = re.sub(r"-\d{4}-\d{2}\.html$", "", path.name)
    is_masherat = slug in EARLY_MASHERAT_CUPS and int(path.name[-12:-8]) <= 1971
    is_league = slug in LEAGUES or is_masherat
    result = winner_from_league(page) if is_league else winner_from_bracket(page)
    if not result and not is_league:
        result = winner_from_single_final(page)
    if not result:
        skipped.append((path.name, "winner not unambiguous"))
        continue
    name, href = result
    label = "CHAMPIONS" if is_masherat else ("LEAGUE CHAMPIONS" if is_league else ("FA CUP WINNERS" if slug == "fa-cup" else "CUP WINNERS"))
    panel = make_panel(name, href, label)
    if not panel:
        skipped.append((path.name, "invalid club link"))
        continue
    # Only insert after a season switcher, preserving all existing content.
    pattern = r'(<div class="season-switcher">.*?</div>)'
    if len(re.findall(pattern, page, re.S)) != 1:
        skipped.append((path.name, "season navigation not found"))
        continue
    page = re.sub(pattern, lambda m: m.group(1) + panel, page, count=1, flags=re.S)
    path.write_text(page, encoding="utf-8")
    changed.append((path.name, name))

print(f"Inserted {len(changed)} winners panels; skipped {len(skipped)} pages.")
for file, reason in skipped:
    print(f"SKIP {file}: {reason}")
(ROOT / "competition-winners-rollout-report.txt").write_text(
    f"Added: {len(changed)}\nSkipped: {len(skipped)}\n\n" +
    "\n".join(f"ADDED {file}: {winner}" for file, winner in changed) +
    "\n\n" + "\n".join(f"SKIP {file}: {reason}" for file, reason in skipped) + "\n",
    encoding="utf-8")
