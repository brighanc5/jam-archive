#!/usr/bin/env python3
"""Fail deployment if public build has missing pages, bad URLs, or developer-only state."""
from pathlib import Path
import json, os, re, sys, xml.etree.ElementTree as ET
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit
root=Path(__file__).resolve().parents[1]
site=root/'site'
origin=os.environ.get('JAM_ARCHIVE_ORIGIN','').rstrip('/')
assert origin.startswith('https://'), 'Set JAM_ARCHIVE_ORIGIN to actual website origin'
assert (site/'index.html').is_file()
assert (site/'404.html').is_file()
assert not list(site.rglob('*.sqlite')), 'Developer databases in public output'
assert not list(site.rglob('*.py')), 'Python source in public output'
assert not list(site.rglob('research_queue.json')), 'Private moderation queue in public output'
class Links(HTMLParser):
    def __init__(self): super().__init__();self.urls=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag in ('a','link','script','img'):
            k='href' if tag in ('a','link') else 'src'
            if k in a:self.urls.append(a[k])
missing=[];n=0
for html in site.rglob('*.html'):
    parser=Links();parser.feed(html.read_text(encoding='utf-8'))
    for href in parser.urls:
        if not href or href.startswith(('#','mailto:','tel:','data:','javascript:','//')):continue
        parsed=urlsplit(href)
        if parsed.scheme:continue
        target=site/unquote(parsed.path.lstrip('/')) if parsed.path.startswith('/') else html.parent/unquote(parsed.path)
        if target.is_dir():target=target/'index.html'
        if not target.exists():
            # Directory without a slash should still resolve via Cloudflare's HTML handling.
            alt=Path(str(target)+'/index.html')
            if not alt.exists():missing.append((str(html.relative_to(site)),href))
        n+=1
assert not missing, f'{len(missing)} broken local links: {missing[:12]}'
ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9'}
urls=[t.text for t in ET.parse(site/'sitemap.xml').findall('s:url/s:loc',ns)]
assert len(urls)==245, f'Unexpected number of sitemap routes: {len(urls)}'
assert all(url.startswith(origin+'/') for url in urls), 'Sitemap points at wrong origin'
assert len(list((site/'artists').glob('*/index.html')))==196
assert len(list((site/'shows').glob('*/index.html')))==9
assert len(list((site/'songs').glob('*/index.html')))==32
assert 'Disallow: /' not in (site/'robots.txt').read_text()
print(f'PUBLIC CHECK PASS: {len(urls)} URLs / {n} checked local HTML references / no private state')
