# Samba for VBR

Goal: share the same Music directory as LMS/ripper so the Mac (rick-laptop24) can read and write files over SMB (e.g. Picard).

## Current status: containerized Samba fails

**In Docker** (custom image or mbentley/samba): session setup (auth) succeeds, but **tree connect fails with NT_STATUS_NO_SUCH_USER** from both the host (`smbclient`) and the Mac. Tried Samba 4.13, 4.15, 4.22; GUEST and nobody; config aligned with host_samba; minimal config (no printers). The failure is consistent in containers; the cause is unclear (registry/passdb lookup in tree connect path?).

## Workaround: run Samba on the host

**Host Samba works.** Use the config in `host_samba/` and run Samba via systemd on the server:

1. Copy the working config:  
   `sudo cp host_samba/smb.conf /etc/samba/smb.conf`  
   (or merge with the host’s existing config so the `[music]` share and macOS options match `host_samba/smb.conf`.)

2. Restart Samba on the host:  
   `sudo systemctl restart smbd nmbd`

3. From the Mac, connect to `smb://newsounds/music` (guest or with credentials as on the host).

So for now: **run the rest of VBR in Docker; run Samba on the host** and keep the samba service in `docker-compose.yml` commented out (or use a compose profile) until the container tree-connect issue is resolved.

## If you retry the container later

- `samba/smb.conf` is aligned with `host_samba/` (vfs_fruit, force user 1000, guest ok, etc.).
- Compose is set up to use **mbentley/samba** with `ACCOUNT_nobody=65534:guest` and the config bind-mounted.
- Test from host: `smbclient //127.0.0.1/music -U 'nobody%guest' -c "ls"` (or trigger map-to-guest with a bad user). If tree connect still returns NT_STATUS_NO_SUCH_USER, the container path is still broken.

## Environment (when reporting the container issue)

- **Host:** Ubuntu 22.04 LTS, kernel 5.15.0-164-generic (x86_64)
- **Docker:** 23.0.1 (build a5ee5b1)
- **Docker Compose:** v2.16.0
- **Runtime:** runc v1.1.4, containerd 2456e98
- **Storage:** overlay2, extfs
- **Security:** apparmor, seccomp (builtin), cgroup v2

## Reference

- **host_samba/** – config that worked when Samba ran on the host; use it for host Samba or to compare with `samba/smb.conf`.
