# Reading LMS logs on newsounds (for debugging Spotty, transcoding, etc.)

Use **`ssh newsounds`** — this machine usually cannot reach your LAN LMS URL, and there is no separate “Spotty-only” log file by default.

## Primary log file (persistent)

Host path (same tree as container `/config`):

```text
/home/rec/Music/state/logs/server.log
```

Also rotated: `server.log.0`, …

## Container stdout (often duplicates server logging)

```bash
docker logs vbr-lms-1 2>&1 | tail -100
```

Use **`server.log`** when you need history or **grep**; use **`docker logs`** for the latest burst after a restart.

## Plugin / Spotty lines

Spotty writes into **`server.log`** with class names like **`Plugins::Spotty`** — there is no separate plugin log path unless you configure one.

Quick filters:

```bash
LOG=/home/rec/Music/state/logs/server.log
grep -iE 'Spotty|spotty|Plugins::Spotty|librespot|spt:|spotify:' "$LOG" | tail -80
grep -iE 'transcod|ffmpeg|flac|ogg|pipeline|stream_s|Warning:|Error:' "$LOG" | tail -80
```

## Faster iteration loop

1. You **start Spotify playback from LMS** (one attempt).
2. Immediately run:

```bash
ssh newsounds 'tail -n 250 /home/rec/Music/state/logs/server.log'
```

Or narrow the window:

```bash
ssh newsounds 'grep -i spotty /home/rec/Music/state/logs/server.log | tail -50'
```

## More detail (UI)

In **LMS web UI** → **Settings → Advanced → Logging** (wording may vary): raise **log level** for **plugins** or search for **spotty** / **network** / **transcoding** and set to **DEBUG**, reproduce once, then **`tail server.log`** again. Reset levels afterward so the log does not grow excessively.

## Scanner log

Separate file if scans misbehave:

```text
/home/rec/Music/state/logs/scanner.log
```
