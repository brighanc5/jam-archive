#!/usr/bin/env python3
"""Local source tree identity test (no network). Use before debugging wrong folders."""
from pathlib import Path
import shutil
import subprocess
import sys
import ast

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = [
    '.github/workflows/verify-static.yml',
    '.github/workflows/daily-research.yml',
    'wrangler.jsonc',
    'RELEASE_VERSION.txt',
    'build_v03.py', 'build_v04.py', 'build_v05.py', 'build_v06.py',
    'build_v061.py', 'build_v07.py', 'build_v08.py', 'build_v09.py', 'build_v010.py', 'build_v011.py', 'build_v012.py', 'build_v013.py',
    'history_seed.py', 'song_paths.js', 'song_paths.css',
    'connections.js', 'connections.css', 'deep_archive.js', 'deep_archive.css', 'data/research_dossiers.json',
    'data/approved_recordings.json', 'data/show_depth_v014.json', 'show_depth.css', 'show_depth.js', 'build_v014.py', 'tests/test_show_depth_v014.py',
    'scripts/build_public.sh', 'scripts/check_public_site.py', 'scripts/polish_site.py', 'jam_look.css', 'jam_experience.js', 'tests/test_v014_experience.py',
    'scripts/safety_check.py', 'tests/test_agent.py',
    'tests/test_publication.py', 'tests/test_contributions.py',
    'tests/test_time_machine.py', 'tests/test_song_paths.py',
    'tests/test_connections.py', 'tests/test_deep_archive.py', 'tests/test_performance_lab.py', 'data/performance_evidence.json', 'data/era_index.json', 'era_atlas.js', 'era_atlas.css', 'tests/test_era_atlas.py',
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
    # The clean Git checkout intentionally has no generated site/ directory.
    # unittest discovery imports tests, and some v0.13 tests load site/assets
    # at module import time. A missing generated asset turns that module into
    # one _FailedTest, incorrectly reporting 80 rather than 91 methods.
    # Inspect test definitions without importing them. The full unittest suite
    # runs AFTER site generation in scripts/build_public.sh.
    count = 0
    test_sources = sorted((ROOT / 'tests').glob('test_*.py'))
    for source in test_sources:
        try:
            tree = ast.parse(source.read_text(encoding='utf-8'), filename=str(source))
        except (SyntaxError, OSError, UnicodeDecodeError) as exc:
            print('TEST SOURCE ERROR:', source.name, exc)
            missing.append(str(source.relative_to(ROOT)))
            continue
        count += sum(
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name.startswith('test_')
            for node in ast.walk(tree)
        )
    print('Test definitions discovered:', count, '(v0.14 expects at least 116; full suite runs after build)')
    # Stop before Python evaluates unresolved Git conflict markers, a previous failure.
    conflict_files = []
    for path in ROOT.rglob('*'):
        if not path.is_file() or path.suffix not in {'.py', '.js', '.css', '.sh', '.yml', '.yaml', '.json', '.jsonc'}:
            continue
        if any(part in {'.git', 'site', '__pycache__'} for part in path.relative_to(ROOT).parts):
            continue
        try:
            lines = path.read_text(encoding='utf-8').splitlines()
        except (UnicodeDecodeError, OSError):
            continue
        if any(line.startswith(('<<<<<<< ', '>>>>>>> ')) or line == '=======' for line in lines):
            conflict_files.append(str(path.relative_to(ROOT)))
    for path in conflict_files:
        print('UNRESOLVED MERGE CONFLICT:', path)
    if missing or conflict_files or 'v0.14' not in version or count < 116 or not shutil.which('node'):
        print('DOCTOR FAILED: check missing source files, test definitions, merge markers, or Node.js.')
        return 1
    print('REPOSITORY DOCTOR PASS: complete v0.14 source, 116+ tests, no Git conflict markers.')
    return 0

if __name__ == '__main__':
    sys.exit(check())
