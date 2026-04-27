#!/usr/bin/env python3
"""Fail if docker-compose.test.yml drifts beyond approved overrides."""
from pathlib import Path
import re
import sys

path = Path("docker-compose.test.yml")
if not path.exists():
    print("ERROR: docker-compose.test.yml not found")
    sys.exit(1)

text = path.read_text()

forbidden = [
    r"\bimage\s*:",
    r"\bbuild\s*:",
    r"\benvironment\s*:",
    r"\bports\s*:",
    r"\bdevices\s*:",
    r"\bextra_hosts\s*:",
    r"\bnetwork_mode\s*:",
    r"\brestart\s*:",
    r"\buser\s*:",
    r"\bhostname\s*:",
]
for pat in forbidden:
    if re.search(pat, text):
        print(f"ERROR: forbidden key in docker-compose.test.yml: /{pat}/")
        sys.exit(1)

allowed_services = {"ripper", "flac_mirror"}
services = set(re.findall(r"^  ([a-zA-Z0-9_-]+):\s*$", text, re.MULTILINE))
extra_services = services - allowed_services
if extra_services:
    print("ERROR: unexpected service(s) in test override:", ", ".join(sorted(extra_services)))
    sys.exit(1)

if re.search(r"^\s*lms:\s*$", text, re.MULTILINE):
    print("ERROR: lms overrides are not allowed in docker-compose.test.yml")
    sys.exit(1)

if "TEST_MUSIC_ROOT" not in text:
    print("ERROR: TEST_MUSIC_ROOT is required in docker-compose.test.yml")
    sys.exit(1)

# Require every volume line in the override to use TEST_MUSIC_ROOT.
for line in text.splitlines():
    if re.match(r"^\s*-\s*", line) and ":/" in line:
        if "TEST_MUSIC_ROOT" not in line:
            print("ERROR: volume override line must use TEST_MUSIC_ROOT:")
            print("  " + line)
            sys.exit(1)

print("OK: docker-compose.test.yml only changes approved ripper/mirror test volume paths.")
