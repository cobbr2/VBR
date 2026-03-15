#!/bin/sh
# Run nmbd in background, then smbd in foreground so the container stays up.
# smbd --debug-stdout so docker logs shows connection activity; debuglevel 2 for diagnostics.
set -e
# Ensure mount point exists so [music] share always has a valid path
mkdir -p /music
# So GUEST can tree-connect to the share, ensure path is traversable
chmod a+rx /music 2>/dev/null || true
# Set domain SID first so passdb lookups work on tree connect
net setdomainsid S-1-5-21-1-1-1 -s /etc/samba/smb.conf 2>/dev/null || true
# Guest maps to nobody; add nobody to passdb so tree connect finds the session user
printf '\n\n' | smbpasswd -a -s nobody 2>/dev/null || \
  printf "guest\nguest\n" | smbpasswd -a -s nobody 2>/dev/null || true
nmbd --daemon --no-process-group --configfile=/etc/samba/smb.conf
exec smbd --foreground --no-process-group --debug-stdout --debuglevel=3 --configfile=/etc/samba/smb.conf
