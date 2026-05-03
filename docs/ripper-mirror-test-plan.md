# Ripper + Mirror Test Plan (newsounds)

Scope: validate `ripper` and `flac_mirror` behavior safely, without polluting production media paths.

Rules:
- Run tests on `newsounds` only.
- Keep LMS on normal config; test override applies only to `ripper` and `flac_mirror`.
- Use `TEST_MUSIC_ROOT` (default `/home/rec/Music_test`) for test outputs.

## 1) Pre-flight

- [ ] Confirm branch/commit on `newsounds` (`git rev-parse --short HEAD`).
- [ ] Confirm test override guard passes:
  - `python3 tools/verify_test_override.py`
- [ ] Ensure test root exists:
  - `/home/rec/Music_test/{flac,mp3,m4a,ogg,playlists,state}`
- [ ] Stop production `ripper`/`flac_mirror` before test run (avoid `/dev/sr0` contention):
  - `docker compose stop ripper flac_mirror`

## 2) Start test-mode services

- [ ] Start test-mode `ripper` and `flac_mirror`:
  - `TEST_MUSIC_ROOT=/home/rec/Music_test docker compose -f docker-compose.yml -f docker-compose.test.yml up -d ripper flac_mirror`
- [ ] Verify binds:
  - `ripper` binds `/home/rec/Music_test:/out`
  - `flac_mirror` binds `/home/rec/Music_test/flac -> /flac`, `/mp3`, `/m4a`, `/ogg`

## 3) Known-good disc test

Use one already-ripped, known-good CD.

- [ ] Insert disc and watch logs:
  - `docker compose logs --tail=200 -f ripper flac_mirror`
- [ ] Confirm FLAC output appears under `/home/rec/Music_test/flac/...`.
- [ ] Confirm mirrored MP3 output appears under `/home/rec/Music_test/mp3/...`.
- [ ] Confirm no crashes/restart loops for either container.
- [ ] Confirm logs are readable (not silent, not overwhelming spam).

## 4) Repeatability / idempotence check

- [ ] Re-run with the same known-good disc.
- [ ] Verify no unexpected duplicate explosions in test directories.
- [ ] Verify mirror does not continuously re-transcode unchanged inputs.

## 5) Error-path checks (optional, recommended)

- [ ] Use a problematic/dirty disc and verify ripper behavior is explicit.
- [ ] Confirm transcode failure logs are specific enough to diagnose track/file.
- [ ] Confirm mirror continues processing other files when one fails.

## 6) Non-regression checks for LMS state safety

These checks guard against collateral LMS regressions while testing ripper/mirror. For a full, repeatable checklist (track count nuance, `extensions.prefs`, Spotty files), use **`docs/lms-restart-checks.md`**.

- [ ] LMS mounts still point to production music/state (`${MUSIC_ROOT:-/home/rec/Music}...`).
- [ ] Favorites count/list unchanged from baseline.
- [ ] **Library:** compare `SELECT COUNT(*) FROM tracks WHERE audio=1` (primary music count), not only raw `tracks` total — the total can differ by 1 if an edge row (`audio IS NULL`) moves; see `lms-restart-checks.md`.
- [ ] Plugin prefs file count unchanged; `extensions.prefs` still lists expected enabled plugins.
- [ ] (Optional) `spotty.prefs` size/checksum if you care about on-disk Spotty config (auth may still need UI re-login after major changes).

## 7) Exit / cleanup

- [ ] Stop test-mode `ripper`/`flac_mirror`:
  - `TEST_MUSIC_ROOT=/home/rec/Music_test docker compose -f docker-compose.yml -f docker-compose.test.yml stop ripper flac_mirror`
- [ ] Restart normal production `ripper`/`flac_mirror`:
  - `docker compose up -d ripper flac_mirror`
- [ ] Optionally clean test artifacts from `/home/rec/Music_test`.

## Useful commands

```bash
# Guard
python3 tools/verify_test_override.py

# Start test mode
TEST_MUSIC_ROOT=/home/rec/Music_test docker compose -f docker-compose.yml -f docker-compose.test.yml up -d ripper flac_mirror

# Observe
TEST_MUSIC_ROOT=/home/rec/Music_test docker compose -f docker-compose.yml -f docker-compose.test.yml ps
TEST_MUSIC_ROOT=/home/rec/Music_test docker compose -f docker-compose.yml -f docker-compose.test.yml logs --tail=200 -f ripper flac_mirror

# Stop test mode
TEST_MUSIC_ROOT=/home/rec/Music_test docker compose -f docker-compose.yml -f docker-compose.test.yml stop ripper flac_mirror
```

## Tonight stop criteria (2026-04-26)

If the known-good CD test succeeds in test mode, stop for tonight and defer Spotty:

- [ ] `ripper` and `flac_mirror` run cleanly against `TEST_MUSIC_ROOT` (`/home/rec/Music_test`).
- [ ] FLAC output appears in test tree, and MP3 mirror output appears as expected.
- [ ] No unexpected duplicate explosion in test output for this run.
- [ ] No stall/restart loop; logs are readable and actionable.
- [ ] Production LMS state remains unchanged (favorites/library/plugin baseline intact).

After these pass:
- [ ] Merge current ripper/mirror work.
- [ ] Next effort: LMS/Lyrion upgrade.
- [ ] Future effort after upgrade: orphan-prune + marker-file feature.

