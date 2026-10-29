#!/usr/bin/env python3
"""Offline exhaustive HTML/accessibility/metadata safety audit for generated routes.

It cannot substitute for a real-browser visual/accessibility test or live-link crawl.
"""
from collections import Counter
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
import json,re,sys,os

ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/'site'
ORIGIN=os.environ.get('JAM_ARCHIVE_ORIGIN','https://thejamarchive.org').rstrip('/')

class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links=[];self.ids=[];self.headings=Counter();self.meta=[];self.viewport=0;self.lang='';self.main=0;self.canonical=[];self.labels=set();self.controls=[];self.labeldepth=0;self.nav=False;self.skip=False;self.images=[];self.badtarget=[];self.iframe=[];self.scripts=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='html':self.lang=a.get('lang','')
        if 'id' in a:self.ids.append(a['id'])
        if tag in ('h1','h2','h3','h4','h5','h6'):self.headings[tag]+=1
        if tag=='main':self.main+=1
        if tag=='label':
            self.labeldepth+=1
            if a.get('for'):self.labels.add(a['for'])
        if tag=='link':
            if a.get('rel')=='canonical':self.canonical.append(a.get('href'))
            if a.get('href'):self.links.append(a['href'])
        if tag=='meta':
            if a.get('name')=='description':self.meta.append(a.get('content',''))
            if a.get('name')=='viewport':self.viewport+=1
        if tag in ('a','img','script'):
            url=a.get('src') if tag in ('img','script') else a.get('href')
            if url:self.links.append(url)
        if tag=='a' and 'ja-skip' in a.get('class','').split():self.skip=True
        if tag=='a' and a.get('target')=='_blank' and not {'noopener','noreferrer'} <= set(a.get('rel','').split()):self.badtarget.append(a.get('href'))
        if tag=='nav' and a.get('aria-label')=='Archive sections':self.nav=True
        if tag=='img' and 'alt' not in a:self.images.append(a.get('src'))
        if tag=='iframe':self.iframe.append(a.get('src'))
        if tag=='script' and a.get('src'):self.scripts.append(a['src'])
        if tag in ('input','select','textarea'):
            if tag=='input' and a.get('type')=='hidden':return
            self.controls.append((tag,a,self.labeldepth>0))
    def handle_endtag(self,tag):
        if tag=='label':self.labeldepth=max(0,self.labeldepth-1)


def run():
    issues=[]; warnings=[];pages=0;links=0;canonical=[];all_ids={}; missing_fragment=[]
    for file in sorted(SITE.rglob('*.html')):
        pages+=1
        rel=str(file.relative_to(SITE))
        html=file.read_text(encoding='utf-8')
        p=Page();p.feed(html)
        all_ids[rel]=set(p.ids)
        if p.lang!='en':issues.append((rel,'missing or unexpected HTML language'))
        if p.main!=1:issues.append((rel,'expected exactly one main landmark'))
        if p.headings['h1']!=1:issues.append((rel,'expected exactly one h1'))
        if p.viewport!=1:issues.append((rel,'expected exactly one responsive viewport meta'))
        if len(p.meta)!=1 or not p.meta[0].strip():issues.append((rel,'missing or duplicate meta description'))
        if len(p.ids)!=len(set(p.ids)):issues.append((rel,'duplicate HTML id'))
        if p.badtarget:issues.append((rel,'unsafe target=_blank without noopener/noreferrer'))
        if p.images:issues.append((rel,'image missing alt attribute'))
        if p.iframe:issues.append((rel,'unreviewed iframe'))
        if any(urlsplit(s).scheme in ('http','https') for s in p.scripts):issues.append((rel,'external script dependency'))
        if not p.skip or 'id="ja-main"' not in html:issues.append((rel,'missing working skip link'))
        if rel!='index.html' and not p.nav:issues.append((rel,'missing consistent section navigation'))
        if rel=='404.html':
            if p.canonical:issues.append((rel,'404 should not have canonical URL'))
            if 'name="robots" content="noindex"' not in html:issues.append((rel,'404 missing noindex'))
        else:
            path='/' if rel=='index.html' else '/'+rel.removesuffix('index.html')
            expected=ORIGIN+path
            if p.canonical!=[expected]:issues.append((rel,'canonical URL mismatch'))
        for tag,attr,wrapped in p.controls:
            if not wrapped and not attr.get('aria-label') and not attr.get('aria-labelledby') and not (attr.get('id') in p.labels):
                issues.append((rel,'unlabeled '+tag+' '+(attr.get('id') or 'anonymous')))
        for uri in p.links:
            parts=urlsplit(uri)
            if parts.scheme or parts.netloc:continue
            if uri.startswith(('mailto:','tel:','data:','javascript:')):continue
            links+=1
            if parts.fragment and parts.path in ('','./'):
                if parts.fragment not in p.ids:missing_fragment.append((rel,parts.fragment))
    # The homepage uses JS routing, and legacy fragment links can target dynamically built views.
    for rel,fragment in missing_fragment:
        if rel!='index.html':issues.append((rel,'broken same-page fragment #'+fragment))
        else:warnings.append((rel,'home SPA fragment not in static HTML #'+fragment))
    public=json.loads((SITE/'assets/catalog.json').read_text(encoding='utf-8'))
    dates=[date.fromisoformat(v['date']) for v in public['events']]
    checked='2026-10-26'
    age=(date.fromisoformat('2026-10-29')-date.fromisoformat(checked)).days
    if not (SITE/'assets/performance-lab.json').is_file():issues.append(('assets','missing performance evidence export'))
    stats={'version':'0.14','scope':'local compiled site, not live website or visual browser audit','html_pages_inspected':pages,'internal_and_fragment_references_seen':links,'issues':len(issues),'warnings':len(warnings),'external_script_dependencies':0,'tour_snapshot_checked':checked,'tour_snapshot_age_at_release_days':age,'dated_events':len(dates),'events_before_release_date':sum(d<date(2026,10,29) for d in dates),'performance_sources_reviewed':'2026-10-29','issue_details':[{'file':f,'problem':x} for f,x in issues[:50]],'warning_details':[{'file':f,'problem':x} for f,x in warnings[:30]],'audit_limitations':['Cannot inspect deployed Cloudflare configuration or HTTP headers','Does not test real-browser interaction, keyboard flow or color contrast','Does not verify external sources remain online or unchanged','Data is an editorial snapshot, not a live ticket feed']}
    (SITE/'assets/site_audit.json').write_text(json.dumps(stats,indent=2)+'\n',encoding='utf-8')
    print('SITE QUALITY AUDIT: '+str(pages)+' HTML pages / '+str(links)+' links visited / '+str(len(issues))+' issues / '+str(len(warnings))+' warnings')
    for f,x in issues[:20]:print('ISSUE',f,x)
    for f,x in warnings[:10]:print('WARNING',f,x)
    return 1 if issues else 0
if __name__=='__main__':sys.exit(run())
