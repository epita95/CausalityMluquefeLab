#!/usr/bin/env python3
"""Build and verify the bilingual CausalityLab website."""
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
quarto = shutil.which('quarto')
if not quarto:
    raise SystemExit('Quarto is required and must be on PATH.')
subprocess.run([quarto, 'render'], cwd=ROOT/'site', check=True)
subprocess.run([sys.executable, str(ROOT/'scripts/verify.py')], check=True)
