#!/usr/bin/env python3
"""Rebuild historical Masherat Cup league tables from recorded match results.
Only updates divisions with complete, internally consistent fixtures.
"""
from collections import defaultdict
from pathlib import Path
import re
import html

ROOT = Path(__file__).resolve().parents[1]
COMP = ROOT / "competitions"
CUPS = ("brados-cup", "denton-cup", "gresdon-cup", "warfield-cup")
report = []
updated_pages = 0
updated_tables = 0
skips = []

for cup in CUPS:
    for path in sorted(COMP.glob(cup + "-*.html")):
        year = int(path.stem[-7:-3])
        if year > 1971:
            continue
        page = path.read_text(encoding="utf-8")
        sections = list(re.finditer(r'<h2\b[^>]*>.*?</h2>', page, re.S))
        replacements = []
        for idx, heading in enumerate(sections):
            begin = heading.end()
            end = sections[idx + 1].start() if idx + 1 < len(sections) else page.find("</main>", begin)
            if end < 0:
                continue
            section = page[begin:end]
            table = re.search(r'<table class="league-table[^"]*">.*?<tbody>(.*?)</tbody></table>', section, re.S)
            if not table:
                continue
            rows = re.findall(r'<tr\b[^>]*>.*?</tr>', table.group(1), re.S)
            clubs = {}
            for row in rows:
                link = re.search(r'<td class="club"><a href="([^"]+)">([^<]+)</a>', row)
                if link:
                    clubs[html.unescape(link.group(2))] = (link.group(1), row)
            if len(clubs) != len(rows) or not clubs:
                skips.append((path.name, heading.group(), "unreadable table"))
                continue
            scores = defaultdict(lambda: [0]*7)  # P W D L GF GA Pts
            games = []
            for match in re.finditer(r'<table class="results"><tbody>(.*?)</tbody></table>', section, re.S):
                for row in re.findall(r'<tr\b[^>]*>(.*?)</tr>', match.group(1), re.S):
                    m = re.fullmatch(r'\s*<td><a href="[^"]+">([^<]+)</a></td><td class="score">(\d+)[–-](\d+)</td><td><a href="[^"]+">([^<]+)</a></td>\s*', row, re.S)
                    if m:
                        a, ga, gb, b = html.unescape(m.group(1)), int(m.group(2)), int(m.group(3)), html.unescape(m.group(4))
                        games.append((a, ga, gb, b))
            if not games or any(a not in clubs or b not in clubs or a == b for a, _, _, b in games):
                skips.append((path.name, heading.group(), "missing or foreign results"))
                continue
            for a, ga, gb, b in games:
                x, y = scores[a], scores[b]
                x[0] += 1; y[0] += 1
                x[4] += ga; x[5] += gb
                y[4] += gb; y[5] += ga
                if ga > gb:
                    x[1] += 1; y[3] += 1; x[6] += 3
                elif ga < gb:
                    y[1] += 1; x[3] += 1; y[6] += 3
                else:
                    x[2] += 1; y[2] += 1; x[6] += 1; y[6] += 1
            # All teams must have completed an equal home-and-away league.
            expected = 2 * (len(clubs) - 1)
            if len(games) != len(clubs) * expected // 2 or any(scores[n][0] != expected for n in clubs):
                skips.append((path.name, heading.group(), f"incomplete fixtures ({len(games)} matches, expected {len(clubs)*expected//2})"))
                continue
            # Keep original ordering for teams perfectly tied on all sporting criteria.
            order = {n:i for i,n in enumerate(clubs)}
            ranked = sorted(clubs, key=lambda n:(-scores[n][6], -(scores[n][4]-scores[n][5]), -scores[n][4], order[n]))
            rebuilt = []
            for pos, name in enumerate(ranked, 1):
                href, original = clubs[name]
                values = scores[name]
                diff = values[4]-values[5]
                marker = ""
                # Only reassign C/R where the original division actually uses those markers.
                if re.search(r'<b>\(C\)</b>', table.group(1)) and pos == 1:
                    marker = " <b>(C)</b>"
                if re.search(r'<b>\(R\)</b>', table.group(1)) and pos == len(ranked):
                    marker = " <b>(R)</b>"
                rowclass = ' class="boundary-relegation"' if pos == len(ranked) and "boundary-relegation" in table.group(1) else ""
                numbers = values[:6] + [diff, values[6]]
                cells = "".join(f'<td>{v}</td>' for v in numbers[:-1])
                # Include signed goal difference, including explicit + for positive.
                gd = f"+{diff}" if diff > 0 else str(diff)
                cells = "".join(f"<td>{v}</td>" for v in values[:6]) + f"<td>{gd}</td><td class=\"pts\">{values[6]}</td>"
                rebuilt.append(f'<tr{rowclass}><td class="pos">{pos}</td><td class="club"><a href="{href}">{html.escape(name)}</a>{marker}</td>{cells}</tr>')
            newtbody = "".join(rebuilt)
            oldtbody = table.group(1)
            if oldtbody != newtbody:
                absolute_start = begin + table.start(1)
                absolute_end = begin + table.end(1)
                replacements.append((absolute_start, absolute_end, newtbody))
                updated_tables += 1
                report.append(f"UPDATED {path.name} / {re.sub('<[^>]*>', '', heading.group())}: {ranked[0]} ({scores[ranked[0]][6]} pts)")
        if replacements:
            for start, end, replacement in reversed(replacements):
                page = page[:start] + replacement + page[end:]
            path.write_text(page, encoding="utf-8")
            updated_pages += 1

report.append(f"\nUpdated {updated_tables} tables across {updated_pages} pages; skipped {len(skips)} divisions.")
report.extend(f"SKIP {file} / {re.sub('<[^>]*>', '', heading)}: {reason}" for file, heading, reason in skips)
(ROOT / "masherat-table-rebuild-report.txt").write_text("\n".join(report)+"\n", encoding="utf-8")
print(f"Updated {updated_tables} tables across {updated_pages} pages; skipped {len(skips)} divisions.")
