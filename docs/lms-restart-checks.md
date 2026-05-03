# LMS post-restart checks (newsounds)

Use after any `docker compose` restart, host reboot, or full-stack `down`/`up` on production — without assuming the UI (Spotify auth, etc.) is still valid.

**Paths** below use production layout: `MUSIC_ROOT` default is `/home/rec/Music` (see `docker-compose.yml`).

## 1) Container and mounts

- [ ] `cd ~/VBR && git status` is clean; `git rev-parse --short HEAD` matches the commit you expect.
- [ ] `docker compose ps` — `lms`, `ripper`, `flac_mirror` are **Up**; `lms` shows **(healthy)** when the image defines a healthcheck.
- [ ] **LMS binds** (from `docker inspect vbr-lms-1`):
  - music: `${MUSIC_ROOT}` → `/mnt/music` (ro)
  - playlists, state: under same `MUSIC_ROOT` tree
- [ ] **Ripper** bind: `MUSIC_ROOT` → `/out` (rw)
- [ ] **flac_mirror** bind: `MUSIC_ROOT`/{flac,mp3,m4a,ogg} and `user: 1000:1000` as in compose

## 2) Health poll (optional but useful)

LMS may sit in `health: starting` for ~30–60s after boot. Either wait for `docker compose ps` to show **(healthy)**, or:

```bash
docker inspect vbr-lms-1 --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}no-healthcheck{{end}}'
```

## 3) Library DB — what to compare

**Primary music count** (stable across restarts unless you add/remove music):

```bash
sqlite3 /home/rec/Music/state/cache/library.db "SELECT COUNT(*) FROM tracks WHERE audio=1;"
```

**Total `tracks` row count** can move by 1 or 2 without meaning you “lost a song” — non-music or odd rows (e.g. test files, `.wav` in `incoming`, `audio IS NULL`) are counted in `tracks` but are not the main library. Track them separately:

```bash
sqlite3 /home/rec/Music/state/cache/library.db "SELECT COUNT(*) FROM tracks WHERE audio IS NULL;"
```

If **only** the `audio IS NULL` count changes, investigate moved/removed edge files, not a mass library loss.

## 4) Favorites and plugin *files*

- [ ] Favorites: count lines / entries in `.../state/prefs/favorites.opml` (or use the UI).
- [ ] Plugin pref **file count:** `ls .../state/prefs/plugin/*.prefs | wc -l` (or compare to your saved baseline).
- [ ] **Enabled plugins** (UI selection) are reflected in `.../state/prefs/plugin/extensions.prefs` under `plugin:` (e.g. Spotty, SqueezeESP32).

## 5) Plugin config vs authentication (e.g. Spotty)

- **On-disk plugin prefs** (e.g. `spotty.prefs`) show that **settings files still exist**; compare size or checksum across restarts if you want a strict diff:

  ```bash
  wc -c /home/rec/Music/state/prefs/plugin/spotty.prefs
  sha256sum /home/rec/Music/state/prefs/plugin/spotty.prefs
  ```

- **Spotify / Spotty session auth** can still be invalid after a restart or upgrade even when files are present. Treat **re-login in the UI** as a separate step; plan to re-verify after the **Lyrion** upgrade.

## 6) Optional: JSON-RPC

The HTTP JSON-RPC API may require a session; for automation, file-based checks above are usually enough. If you add a small authenticated script later, keep it in-repo next to this doc.

## See also

- `docs/ripper-mirror-test-plan.md` — section 6 (LMS non-regression while testing ripper/mirror).
- `docs/lyrion-docker-persistence-plan.md` (in **homer** repo) — migration to Lyrion 9.x and `/config` layout.
