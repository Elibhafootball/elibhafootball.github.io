#!/usr/bin/env python3
"""Install the shared games-played league-position chart on league season pages."""
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]
COMP=ROOT/'competitions'
LEAGUES=('alpha-league','beta-league','gamma-league','mainland-league','islands-league','mainland-first-division','islands-first-division')
STYLE='''<style>
.position-chart-section{margin:2rem 0 2.5rem}
.position-chart-help{color:#697584;font-size:.9rem}
.position-chart-scroll{overflow-x:auto;max-width:100%;border:1px solid #d9dfe6;border-radius:8px;background:#fff}
.position-chart-inner{position:relative;min-width:850px;padding:12px}
.position-chart-svg{display:block;width:100%;overflow:visible}
.position-chart-tooltip{position:absolute;z-index:2;top:3px;padding:7px 10px;background:#192536;color:white;border-radius:5px;font-size:13px;pointer-events:none;white-space:nowrap}
@media(max-width:700px){.position-chart-inner{min-width:900px}.position-chart-help{font-size:.85rem}}
</style><script src="../league-position-chart.js" defer></script>'''
changed=0
skipped=[]
for page in sorted(COMP.glob('*.html')):
    if not any(re.fullmatch(re.escape(prefix)+r'-\d{4}-\d{2}\.html',page.name) for prefix in LEAGUES):
        continue
    content=page.read_text(encoding='utf-8')
    if 'league-position-chart.js' in content:
        continue
    if 'class="round-block"' not in content or 'class="live-table"' not in content or '</head>' not in content:
        skipped.append(page.name)
        continue
    page.write_text(content.replace('</head>',STYLE+'</head>',1),encoding='utf-8')
    changed+=1
print(f'Added league position chart to {changed} season pages; skipped {len(skipped)} without suitable data')
for name in skipped: print('SKIPPED:',name)

# This script is safe to rerun; existing chart inclusions are preserved.
