"""House style invariants: the palette pass is stable and actually reached every stylesheet."""
from pathlib import Path
import colorsys
import random
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'site'
SRC = (ROOT / 'scripts' / 'house_style.py').read_text(encoding='utf-8')
_ns = {'colorsys': colorsys, 're': re}
exec(SRC[SRC.index('HUE_MAP = ['):SRC.index('def recolor(text)')], _ns)
remap_rgb = _ns['remap_rgb']


class HouseStyleTests(unittest.TestCase):
    def test_remap_is_idempotent(self):
        rng = random.Random(7)
        for _ in range(5000):
            c = tuple(rng.randrange(256) for _ in range(3))
            once = remap_rgb(*c)
            self.assertLessEqual(max(abs(a - b) for a, b in zip(once, remap_rgb(*once))), 1, c)

    def test_no_off_palette_purples_or_limes_left_in_page_css(self):
        hexes = re.compile(r'#([0-9a-fA-F]{6})\b')
        for css in (SITE / 'assets').glob('*.css'):
            for v in hexes.findall(css.read_text(encoding='utf-8')):
                r, g, b = (int(v[i:i + 2], 16) for i in (0, 2, 4))
                h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
                if s < 0.10 or l < 0.03 or l > 0.97:
                    continue
                deg = h * 360
                self.assertFalse(230 <= deg < 322 or 55 <= deg < 100, f'{css.name}: #{v}')

    def test_eyebrows_are_not_shouting(self):
        for page in ('index.html', 'connections/index.html', 'trails/banjo-to-saxophone/index.html'):
            html = (SITE / page).read_text(encoding='utf-8')
            for label in re.findall(r'class="eyebrow">([^<]+)<', html):
                self.assertFalse(label.isupper() and len(label) > 3, f'{page}: {label}')


if __name__ == '__main__':
    unittest.main()
