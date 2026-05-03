# Backlog (future work)

Items we want to track but are not actively implementing yet.

## Player / playlist state after full compose restart

**Observed (2026-05):** After `docker compose down` then `up -d`, players come back online but the **current playlist / playback context** reverts to an **older** state (e.g. Office player twice resumed a **KFJC** favorite instead of what had been playing more recently).

**Desired:** After a host/container restart, players would ideally restore **the same state as before** the restart—including **now playing** and queue—when that is technically feasible with LMS persistence.

**Notes:** Separate from mount/state path bugs; likely involves **what LMS persists** for player state vs favorites, and whether a **full stack** down/up clears something that a simple **LMS-only** restart does not.
