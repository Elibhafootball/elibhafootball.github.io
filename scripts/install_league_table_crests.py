#!/usr/bin/env python3
"""Add compact crests to final tables on all league-season pages."""
from pathlib import Path
import re
root=Path(__file__).resolve().parents[1]/'competitions'
prefixes=('alpha-league','beta-league','gamma-league','mainland-league','islands-league','mainland-first-division','islands-first-division')
style='<style>.league-table.tidy td.club .league-club-crest{display:inline-block;width:16px;height:16px;object-fit:contain;vertical-align:-3px;margin-right:6px;max-width:none;flex:none}</style>'
pages=0
crests=0
skipped=[]
for page in sorted(root.glob('*.html')):
    if not any(re.fullmatch(re.escape(prefix)+r'-\d{4}-\d{2}\.html',page.name) for prefix in prefixes):
        continue
    source=page.read_text(encoding='utf-8')
    start=source.find('<h2>Final table</h2>')
    if start<0:
        skipped.append(page.name+': no final table')
        continue
    table_start=source.find('<table class="league-table tidy"',start)
    table_end=source.find('</table>',table_start)
    if table_start<0 or table_end<0:
        skipped.append(page.name+': table structure not found')
        continue
    part=source[table_start:table_end]
    def add_crest(match):
        global crests
        href=match.group(2)
        # Club pages can be season-specific, but crest filenames are based on the club slug.
        slug=href.rsplit('/',1)[-1].removesuffix('.html')
        crests+=1
        return match.group(1)+f'<img class="league-club-crest" src="../clubs/crests/{slug}.png" alt="" aria-hidden="true" loading="lazy"/>'+match.group(3)
    updated,n=re.subn(r'(<td class="club">)(<a href="([^"]+)"[^>]*>)',lambda m: add_crest(m) if 'league-club-crest' not in part[max(0,m.start()-120):m.start()] else m.group(0),part)
    if not n:
        skipped.append(page.name+': no club links')
        continue
    new=source[:table_start]+updated+source[table_end:]
    if 'league-club-crest' not in source and '</head>' in new:
        new=new.replace('</head>',style+'</head>',1)
    if new!=source:
        page.write_text(new,encoding='utf-8')
        pages+=1
print(f'Updated {pages} season pages with {crests} crests')
for item in skipped:print('SKIPPED:',item)

# Re-runnable; only league-season final tables are modified.
