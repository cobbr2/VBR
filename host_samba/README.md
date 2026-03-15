# Host Samba config (from newsounds)

Reference config for the Music share. Deploy to `/etc/samba/smb.conf` on the server.

## macOS warning: "some services use vfs_fruit, others don't"

All shares that might be used from a Mac ([printers], [print$], [music]) use the same `vfs objects = fruit streams_xattr` so the warning goes away.

## Picard "Permission denied" on recently ripped files

Samba uses `force user = rec` for the [music] share, so every file access is done as Unix user `rec` (uid 1000). On newsounds, the ripper writes as **1001:docker** (and some of `/home/rec/Music/flac` is **root:root**). Even when "others" have read, the Mac client (or vfs_fruit opening resource forks/xattr) can hit permission checks that fail. Making **rec** own everything under Music avoids that.

**Fix on the server:**

1. **One-time fix for existing files** (run as root or with sudo):
   ```bash
   sudo chown -R rec:rec /home/rec/Music
   ```
   Then restart Samba and try Picard again:
   ```bash
   sudo systemctl restart smbd nmbd
   ```

2. **Ongoing: make the ripper write as `rec`** so new rips are owned by rec. On newsounds `rec` is uid=1000, gid=1000. In `docker-compose.yml` the ripper uses `USER_ID=${USER}` / `GROUP_ID=${USER}` — ensure the yar entrypoint resolves that to **numeric** 1000 (or set explicitly). Alternatively add to the ripper service:
   ```yaml
   user: "1000:1000"
   ```
   so the container process runs as 1000:1000 and new files under the Music bind-mount are owned by `rec`.
