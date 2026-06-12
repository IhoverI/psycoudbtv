#!/usr/bin/env python3
"""Build the site-packages-style distribution zip for psycoudbtv.

The resulting archive contains a single top-level ``psycoudbtv/`` directory and
can be unzipped directly into a Python environment's ``site-packages`` (no pip,
no compilation; the package is pure Python and architecture independent).

All entries use forward slashes so the archive extracts correctly on
Linux/macOS. (Windows' ``Compress-Archive`` writes backslash separators, which
Linux treats as literal filenames and therefore fails to expand into folders.)
"""
import os
import re
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY_RANGE = "py3.8-3.13"


def get_version():
    with open(os.path.join(ROOT, "pyproject.toml"), encoding="utf-8") as f:
        text = f.read()
    m = re.search(r'^version\s*=\s*"([^"]+)"', text, re.M)
    return m.group(1) if m else "0.0.0"


def main():
    version = get_version()
    dist = os.path.join(ROOT, "dist")
    os.makedirs(dist, exist_ok=True)
    zip_path = os.path.join(dist, f"psycoudbtv-{version}-{PY_RANGE}.zip")
    if os.path.exists(zip_path):
        os.remove(zip_path)

    pkg_root = os.path.join(ROOT, "psycoudbtv")
    count = 0
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for base, dirs, files in os.walk(pkg_root):
            dirs[:] = [d for d in dirs if d != "__pycache__"]
            for fn in files:
                if fn.endswith((".pyc", ".pyo")):
                    continue
                full = os.path.join(base, fn)
                arc = os.path.relpath(full, ROOT).replace(os.sep, "/")
                z.write(full, arc)
                count += 1

    with zipfile.ZipFile(zip_path) as z:
        bad = [n for n in z.namelist() if "\\" in n]
        if bad:
            raise SystemExit(f"ERROR: backslash entries found: {bad[:3]}")

    print(f"wrote {count} files -> {zip_path}")
    print("OK: all entries use forward slashes")


if __name__ == "__main__":
    main()
