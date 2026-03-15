#!/bin/sh
# Run nmbd in background, then smbd in foreground so the container stays up.
# smbd --debug-stdout so docker logs shows connection activity; debuglevel 2 for diagnostics.
set -e
# Ensure mount point exists so [music] share always has a valid path
mkdir -p /music
# Add GUEST to Samba passdb (empty password so Mac "Guest" with no password works)
printf '\n\n' | smbpasswd -a -s GUEST 2>/dev/null || \
  printf "guest\nguest\n" | smbpasswd -a -s GUEST 2>/dev/null || true
nmbd --daemon --no-process-group --configfile=/etc/samba/smb.conf
exec smbd --foreground --no-process-group --debug-stdout --debuglevel=2 --configfile=/etc/samba/smb.conf
