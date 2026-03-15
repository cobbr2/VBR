# Samba container for VBR

Shares the same Music directory as LMS and the ripper so Mac/Windows clients (e.g. Picard) can read and write files over SMB.

- **Share:** `music` → path `/music` in container (bind-mounted from host `$HOME/Music`).
- **Config:** `smb.conf` uses `force user = 1000` so all access runs as the host user (rec on Ubuntu).
- **macOS:** vfs_fruit + fruit:posix_rename so Finder/Picard can move, delete, and write.

**Before starting:** If Samba is installed on the host, stop it so the container can bind to 139/445 and 137/138:

```bash
sudo systemctl stop smbd nmbd
# or disable: sudo systemctl disable --now smbd nmbd
```

Then bring up the stack (or just the samba service):

```bash
docker compose up -d samba
```

Connect from a Mac: `smb://newsounds/music` (or the host’s hostname if different).
