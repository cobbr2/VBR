# Agent notes for VBR

- **SSH:** You can ssh to `newsounds` (or, when needed, `sounds`) directly without a password to check docker status and run commands.

- **Where we run things:** We do **not** run the stack locally. We keep the source here and use **newsounds for all testing** (deploy there, run `docker compose` there, verify there).

- **Workflow:** We keep the source in this repo and make changes via **GitHub pushes and branches**. When we start a new effort (e.g. a bug fix or feature), we start a new branch for it. Once it works on newsounds, we merge to master.

- **Target client:** The Mac we need to connect is the highest priority: **rick-laptop24**. It runs Tahoe 26.3.1 and is M2-based.

- **Reference config:** The settings in `host_samba/` were successful in letting the Mac (rick-laptop24) edit files in the Music tree when Samba ran on the host.

- **Samba in Docker:** Containerized Samba (custom or mbentley image) currently fails with NT_STATUS_NO_SUCH_USER on tree connect (auth succeeds). Use **host Samba** with `host_samba/smb.conf` as the working approach until that is resolved. See `samba/README.md`.

- **Goals** 
    - Run "newsounds" as the primary LMS server / ripper / mirror on our network.
    - Also have it serve filesystems that allow editing the music collection.
    - Extend this configuration of file shares to two more filesystems (Pictures and Stuff) that currently only exist on "sounds"
    - Have "sounds" as a backup, identical configuration.  Use file synchronization to keep them in sync
    - Make the configuration of both hosts be completely infrastructure-as-code on Github
    - Automate the backup of both servers.

- **Nongoals**
    - Filesystem sharing can be done with anything; samba is what's working now.
