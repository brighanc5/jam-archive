#!/usr/bin/env python3
"""House style: one palette, one type system, one voice across every page.

Runs last in the finishing passes (after site_nav.py). No network. Idempotent:
every mapping lands on a hue (or a capped saturation) that maps to itself.

The site grew 14 layers of page-specific CSS, each with its own hard-coded
purples, limes and pinks. Instead of hand-editing hundreds of hex codes, this
pass maps every colour onto the house palette by hue family:

  purple/violet  -> walnut brown (the room)       lime/yellow-green -> marquee amber
  pink/magenta   -> setlist-marker red            green             -> dark olive-amber
  teal/blue      -> faded denim                   oranges, golds, greys -> unchanged

jam_look.css is written directly in the house palette and is not remapped.
To change the look, edit jam_look.css and the HUE_MAP below. Nothing else.

It also:
  * ships the self-hosted fonts (static/fonts -> /assets/fonts),
  * drops internal taxonomy labels ("ARCHIVE ATLAS / SOURCE-INDEXED DATE",
    "NEW · v0.12") and sentence-cases the eyebrow labels worth keeping,
  * strips the decorative arrows from button and link text (↗ on outbound
    links stays, because it means something).
"""
from pathlib import Path
import colorsys
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'site'
assert (SITE / 'index.html').exists(), 'house_style: build the site first'

# ---- fonts -------------------------------------------------------------
fonts = SITE / 'assets' / 'fonts'
fonts.mkdir(parents=True, exist_ok=True)
for f in (ROOT / 'static' / 'fonts').iterdir():
    shutil.copyfile(f, fonts / f.name)

# ---- palette remap -----------------------------------------------------
# (lo, hi) hue in degrees -> (new hue, saturation factor, saturation cap, lightness factor)
HUE_MAP = [
    ((230, 322), (24, 0.62, 0.42, 1.0)),    # purple -> walnut
    ((322, 368), (5, 1.0, 0.80, 1.0)),    # pink/magenta/red -> marker red
    ((55, 100), (38, 1.0, 0.86, 0.93)),     # lime -> marquee amber
    ((100, 165), (34, 0.55, 0.40, 1.0)),    # green -> olive-amber
    ((165, 230), (198, 1.0, 0.45, 1.0)),   # teal/cyan -> denim
]


def remap_rgb(r, g, b):
    h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
    if s < 0.10 or l < 0.03 or l > 0.97:
        return r, g, b
    deg = h * 360
    for (lo, hi), (nh, sf, cap, lf) in HUE_MAP:
        d = deg + 360 if deg < lo and lo >= 322 else deg
        if lo <= d < hi:
            nr, ng, nb = colorsys.hls_to_rgb(nh / 360, min(1, l * lf), min(s * sf, cap))
            return round(nr * 255), round(ng * 255), round(nb * 255)
    return r, g, b


HEX = re.compile(r'#([0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{3})(?![0-9a-zA-Z_-])')
RGB = re.compile(r'rgba?\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*([,/][^)]*)?\)')


def _hex(m):
    v = m.group(1)
    if len(v) == 3:
        v = ''.join(c * 2 for c in v)
    alpha = v[6:] if len(v) == 8 else ''
    r, g, b = (int(v[i:i + 2], 16) for i in (0, 2, 4))
    return '#%02x%02x%02x%s' % (*remap_rgb(r, g, b), alpha)


def _rgb(m):
    r, g, b = (min(255, int(x)) for x in m.group(1, 2, 3))
    nr, ng, nb = remap_rgb(r, g, b)
    rest = m.group(4) or ''
    return ('rgba(%d,%d,%d%s)' if rest else 'rgb(%d,%d,%d)') % ((nr, ng, nb, rest) if rest else (nr, ng, nb))


def recolor(text):
    return RGB.sub(_rgb, HEX.sub(_hex, text))


STYLE_BLOCK = re.compile(r'(<style[^>]*>)(.*?)(</style>)', re.S)
STYLE_ATTR = re.compile(r'''((?:style|fill|stroke|stop-color|color)=")([^"]*)(")''')


def recolor_html(html):
    html = STYLE_BLOCK.sub(lambda m: m.group(1) + recolor(m.group(2)) + m.group(3), html)
    return STYLE_ATTR.sub(lambda m: m.group(1) + recolor(m.group(2)) + m.group(3), html)


# ---- voice -------------------------------------------------------------
EYEBROW = re.compile(r'(<(div|p|span) class="(?:eyebrow|sd-tag|tm-kicker)">)([^<]*)(</\2>)')
KEEP_CASE = ['Family Tree', 'Jam Archive', 'Grateful Dead', 'Phish', 'Show Passport']


def eyebrow(m):
    text = m.group(3).strip()
    # Internal taxonomy and version stamps tell a fan nothing. Drop them.
    if ' / ' in text or re.search(r'\bv0\.\d', text) or text.lower() in {
            'trust infrastructure', 'the agent workflow', 'test fixtures', 'archive protocol',
            'the archive project', 'specialist source directory'}:
        return ''
    if text.isupper() and ' ' in text:  # leave abbreviations like SBD alone
        text = text[0] + text[1:].lower()
        for k in KEEP_CASE:
            text = re.sub(re.escape(k), k, text, flags=re.I)
    return m.group(1) + text + m.group(4)


ARROW_END = re.compile(r'\s*→\s*(</(?:a|button)>)')


def voice(html):
    html = html.replace('THE <span>JAM</span> ARCHIVE', 'The Jam Archive')
    html = EYEBROW.sub(eyebrow, html)
    return ARROW_END.sub(r'\1', html)


# ---- apply -------------------------------------------------------------
css = js = pages = 0
for f in (SITE / 'assets').glob('*.css'):
    if f.name == 'jam-look.css':
        continue
    f.write_text(recolor(f.read_text(encoding='utf-8')), encoding='utf-8')
    css += 1
for f in (SITE / 'assets').glob('*.js'):
    src = f.read_text(encoding='utf-8')
    out = recolor(src)
    if out != src:
        f.write_text(out, encoding='utf-8')
        js += 1
for f in SITE.rglob('*.html'):
    src = f.read_text(encoding='utf-8')
    out = voice(recolor_html(src))
    if out != src:
        f.write_text(out, encoding='utf-8')
    pages += 1
print(f'HOUSE STYLE PASS: palette + voice on {pages} pages, {css} stylesheets, {js} scripts; fonts shipped')
