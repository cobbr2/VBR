#!/bin/sh
# Run nmbd in background, then smbd in foreground so the container stays up.
set -e
nmbd --daemon --no-process-group --configfile=/etc/samba/smb.conf
exec smbd --foreground --no-process-group --configfile=/etc/samba/smb.conf
