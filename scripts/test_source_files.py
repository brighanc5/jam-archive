#!/usr/bin/env python3
"""Tests source-tree integrity without importing tests or requiring prebuilt site."""
from pathlib import Path
import ast,sys
root=Path(__file__).resolve().parents[1]
for rel in ('build_v014.py','scripts/polish_site.py'):
 ast.parse((root/rel).read_text(encoding='utf-8'))
for rel in ('jam_look.css','jam_experience.js','show_depth.js','data/show_depth_v014.json','tests/test_v014_experience.py'):
 assert (root/rel).is_file(),rel
print('v0.14 source files present')
