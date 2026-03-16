# Agent notes for VBR

- **SSH:** You can ssh to `newsounds` (or, when needed, `sounds`) directly without a password to check docker status and run commands.

- **Workflow:** We use branches for new features. Once a feature works, we merge to master.

- **Target client:** The Mac we need to connect is the highest priority: **rick-laptop24**. It runs Tahoe 26.3.1 and is M2-based.

- **Reference config:** The settings in `host_samba/` were successful in letting the Mac (rick-laptop24) edit files in the Music tree when Samba ran on the host.

- **Samba in Docker:** Containerized Samba (custom or mbentley image) currently fails with NT_STATUS_NO_SUCH_USER on tree connect (auth succeeds). Use **host Samba** with `host_samba/smb.conf` as the working approach until that is resolved. See `samba/README.md`.
