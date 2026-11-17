#!/usr/bin/env python3
"""Install results below existing knockout diagrams; no external spreadsheet access."""
from pathlib import Path
import re
from html import escape, unescape
from collections import OrderedDict

ROOT = Path("competitions")
CUPS = ("fa-cup", "denton-cup", "brados-cup", "warfield-cup",
        "gresdon-cup", "errol-bacchus-shield")
TITLE = re.compile(r'<text class="round-title"[^>]*x="([^"]+)"[^>]*>([^<]+)</text>')
CARD = re.compile(r'<g class="tie-card">([\s\S]*?)</g>')
TEAM = re.compile(r'<a href="([^"]+)"><text class="team([^"]*)"[^>]*>([^<]+)</text></a><text class="score[^"]*"[^>]*>([^<]+)</text>')
RECT = re.compile(r'<rect[^>]*x="([^"]+)"')
SCORE = re.compile(r'^(\d+)(?:\s+(\d+))?(?:\s+\((\d+)\))?')
CSS = '<style>#cup-match-results{margin-top:2rem}#cup-match-results .round-results-column{width:100%;max-width:900px}#cup-match-results table.results{width:100%}#cup-match-results .cup-penalty-note td{font-size:.9em;opacity:.85;padding-top:0;padding-bottom:.65rem;font-style:italic}</style>'
def row(home, away, score, note=""):
    def link(team):
        return '<a href="'+escape(team["href"],quote=True)+'">'+escape(team["name"])+'</a>'
    s = '<tr><td>'+link(home)+'</td><td class="score">'+escape(score)+'</td><td>'+link(away)+'</td></tr>'
    if note:
        s += '<tr class="cup-penalty-note"><td colspan="3"><em>'+escape(note)+'</em></td></tr>'
    return s
def section(title, items):
    return '<div class="round-block"><div class="round-results-column"><h3>'+escape(title)+'</h3><table class="results"><tbody>'+''.join(items)+'</tbody></table></div></div>'
def run(path):
    html = path.read_text(encoding="utf-8")
    if 'id="cup-match-results"' in html:
        return "existing", 0
    titles = [(float(x),unescape(n)) for x,n in TITLE.findall(html)]
    cards = CARD.findall(html)
    if not titles or not cards:
        raise ValueError("Missing expected SVG titles or tie cards")
    groups = OrderedDict((name,[]) for x,name in titles)
    for card in cards:
        rect = RECT.search(card)
        teams = TEAM.findall(card)
        if not rect or len(teams)!=2:
            raise ValueError("Unparseable tie card")
        x = float(rect.group(1))+117
        round_name = min(titles,key=lambda item:abs(item[0]-x))[1]
        pair = [{"href":href,"name":unescape(name).replace(" (p)","").strip(),
                 "winner":"winner" in css,"score":score.strip()} for href,css,name,score in teams]
        parsed = [SCORE.match(t["score"]) for t in pair]
        if any(p is None for p in parsed):
            raise ValueError("Unparseable score")
        first,second = parsed
        replay = bool(first.group(2) and second.group(2))
        winner = next((t for t in pair if t["winner"]),None)
        note = ""
        if first.group(3) and second.group(3):
            if not winner:
                raise ValueError("Penalty shootout without winner")
            index = pair.index(winner)
            note = winner["name"]+" won "+parsed[index].group(3)+"–"+parsed[1-index].group(3)+" on penalties"
        elif first.group(1)==second.group(1) and not replay and winner:
            note = winner["name"]+" won on penalties"
        elif first.group(1)==second.group(1) and not replay and not winner:
            raise ValueError("Draw without advancement information")
        primary = row(pair[0],pair[1],first.group(1)+"–"+second.group(1),note)
        reverse = row(pair[1],pair[0],second.group(2)+"–"+first.group(2)) if replay else None
        groups[round_name].append((primary,reverse))
    output = '<section id="cup-match-results"><h2>Results</h2>'
    n = 0
    for name,matches in groups.items():
        if not matches: continue
        output += section(name,[m[0] for m in matches])
        n += len(matches)
        replays = [m[1] for m in matches if m[1]]
        if replays:
            output += section(name+" Replays",replays)
            n += len(replays)
    output += '</section>'
    if '</main>' not in html:
        raise ValueError("Missing main closing tag")
    html = html.replace('</head>',CSS+'</head>',1).replace('</main>',output+'</main>',1)
    path.write_text(html,encoding="utf-8")
    return "updated",n

def eligible(path):
    name=path.name
    m=re.match(r'^(.+)-(\d{4})-(\d{2})\.html$',name)
    if not m or m.group(1) not in CUPS: return False
    cup,year=m.group(1),int(m.group(2))
    return year>=1970 if cup=="fa-cup" else year>=1972 if cup in ("denton-cup","brados-cup","warfield-cup","gresdon-cup") else True

def main():
    updated=existing=matches=0
    failures=[]
    for path in sorted(ROOT.glob("*.html")):
        if not eligible(path):continue
        try:
            status,n=run(path)
            if status=="updated":updated+=1;matches+=n
            else:existing+=1
        except Exception as e:
            failures.append(f"{path}: {e}")
    print(f"Updated {updated} cup season pages; retained {existing} previously updated pages; added {matches} match results")
    print("Governor's Cup seasons already contain their own leg-by-leg results and are preserved")
    if failures:
        print("Pages requiring manual review:",*failures,sep="\n")
        print(f"Skipped {len(failures)} pages requiring separate treatment; other pages will still be committed")
if __name__=="__main__":
    main()
