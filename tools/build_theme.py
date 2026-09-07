#!/usr/bin/env python3
"""Regenerate, validate, and package the Chrome theme."""

from __future__ import annotations

import json
import subprocess
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist" / "rose-pine-afterglow-chrome-theme.zip"


def main() -> None:
    subprocess.run([sys.executable, str(ROOT / "tools/generate_assets.py")], check=True)
    manifest = json.loads((ROOT / "manifest.json").read_text())
    referenced = [*manifest["icons"].values(), *manifest["theme"]["images"].values()]
    for relative in referenced:
        path = ROOT / relative
        if not path.is_file():
            raise SystemExit(f"Missing referenced asset: {relative}")
        if path.suffix == ".png" and path.read_bytes()[:8] != b"\x89PNG\r\n\x1a\n":
            raise SystemExit(f"Invalid PNG asset: {relative}")

    DIST.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(DIST, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        archive.write(ROOT / "manifest.json", "manifest.json")
        for relative in sorted(referenced):
            archive.write(ROOT / relative, relative)
    print(f"Built and validated {DIST}")


if __name__ == "__main__":
    main()
