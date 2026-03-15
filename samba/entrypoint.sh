#!/bin/sh
# Run nmbd in background, then smbd in foreground so the container stays up.
# smbd --log-stdout so docker logs shows connection activity; debuglevel 2 for diagnostics.
set -e
# Ensure mount point exists so [music] share always has a valid path
mkdir -p /music
nmbd --daemon --no-process-group --configfile=/etc/samba/smb.conf
exec smbd --foreground --no-process-group --debug-stdout --debuglevel=2 --configfile=/etc/samba/smb.conf
