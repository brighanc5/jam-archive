#!/usr/bin/env python3
"""Local source tree identity test (no network). Use before debugging wrong folders."""
from pathlib import Path
import shutil
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = [
    '.github/workflows/verify-static.yml',
    '.github/workflows/daily-research.yml',
    'wrangler.jsonc',
    'RELEASE_VERSION.txt',
    'build_v03.py', 'build_v04.py', 'build_v05.py', 'build_v06.py',
    'build_v061.py', 'build_v07.py', 'build_v08.py', 'build_v09.py',
    'history_seed.py', 'song_paths.js', 'song_paths.css',
    'data/approved_recordings.json',
    'scripts/build_public.sh', 'scripts/check_public_site.py',
    'scripts/safety_check.py', 'tests/test_agent.py',
    'tests/test_publication.py', 'tests/test_contributions.py',
    'tests/test_time_machine.py', 'tests/test_song_paths.py',
]

def check():
    print('=== JAM ARCHIVE REPOSITORY DOCTOR ===')
    print('Folder:', ROOT)
    missing = [f for f in EXPECTED if not (ROOT / f).is_file()]
    for name in missing:
        print('MISSING:', name)
    version = (ROOT / 'RELEASE_VERSION.txt').read_text(encoding='utf-8') if (ROOT / 'RELEASE_VERSION.txt').is_file() else ''
    print('Release marker:', version.splitlines()[0] if version else 'MISSING')
    git = shutil.which('git')
    if git:
        result = subprocess.run([git, 'rev-parse', '--show-toplevel'], cwd=ROOT, capture_output=True, text=True)
        if result.returncode == 0:
            print('Git repository root:', result.stdout.strip())
            if Path(result.stdout.strip()).resolve() != ROOT:
                print('WARNING: files are not at the Git repository root')
        else:
            print('NOTE: This folder is not itself a Git clone. That is fine in the extracted ZIP; merge into the GitHub Desktop folder before committing.')
    else:
        print('NOTE: git is unavailable; use GitHub Desktop to confirm the repository folder.')
    for tool in ('python3', 'node'):
        print(tool + ':', shutil.which(tool) or 'MISSING')
    loader = unittest.TestLoader()
    try:
        suite = loader.discover(str(ROOT / 'tests'), pattern='test_*.py')
        count = suite.countTestCases()
    except Exception as exc:
        print('TEST DISCOVERY ERROR:', exc)
        count = 0
    print('Tests discovered:', count, '(v0.9 expects at least 37)')
    if missing or 'v0.9' not in version or count < 37 or not shutil.which('node'):
        print('DOCTOR FAILED: probably incomplete file copy, wrong folder, or missing Node.js.')
        return 1
    print('REPOSITORY DOCTOR PASS: complete v0.9 source tree and test suite detected.')
    return 0

if __name__ == '__main__':
    sys.exit(check())
