#!/usr/bin/env python3
"""Reproducible origin-aware v0.6.1 launch build; do not invent URLs."""
from pathlib import Path
from html import escape
import os, subprocess, sys, re, xml.etree.ElementTree as ET
root=Path(__file__).resolve().parent
origin=os.environ.get('JAM_ARCHIVE_ORIGIN','').strip().rstrip('/')
if not re.fullmatch(r'https://[A-Za-z0-9.-]+(?::\d+)?',origin):
    raise SystemExit('Set JAM_ARCHIVE_ORIGIN to your actual verified HTTPS site origin')
subprocess.run([sys.executable,str(root/'build_v06.py')],cwd=root,check=True)
site=root/'site'
# The v0.6 builder handles canonical links for the generated profiles, songs and concert dossiers.
# Add them to custom pages and the homepage; avoid duplicate canonical links.
for rel, canonical in [('index.html','/'),('about/index.html','/about/'),('contribute/index.html','/contribute/')]:
    path=site/rel
    html=path.read_text(encoding='utf8')
    if 'rel="canonical"' not in html:
        html=html.replace('</head>',f'<link rel="canonical" href="{escape(origin+canonical,quote=True)}"><meta property="og:url" content="{escape(origin+canonical,quote=True)}"></head>',1)
    path.write_text(html,encoding='utf8')
# v0.6 adds the About route to the v0.5 generated XML. Assert all public HTML routes are indexed.
ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9'}
tree=ET.parse(site/'sitemap.xml')
urls={el.text for el in tree.findall('s:url/s:loc',ns)}
for p in site.rglob('index.html'):
    expected=origin+'/' + str(p.parent.relative_to(site)).replace('\\','/').strip('./')
    expected=expected.rstrip('/')+'/'
    assert expected in urls,(p,expected)
print('Origin-aware canonical and sitemap checks passed:',len(urls),'URLs')
