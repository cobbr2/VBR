# Samba in container for VBR Music share. Uses full Samba (incl. vfs_fruit) for macOS.
FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update -y && \
    apt-get install -y --no-install-recommends samba smbclient && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Dirs required by smb.conf (printers/print$ and logs). /music is the mount point.
# System user "guest" so macOS GUEST authentication has a real account.
RUN mkdir -p /var/spool/samba /var/lib/samba/printers /var/log/samba /music && \
    chmod 1777 /var/spool/samba && \
    useradd -r -s /bin/false -d /nonexistent guest

COPY smb.conf /etc/samba/smb.conf
COPY usermap /etc/samba/usermap
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 139 445
EXPOSE 137/udp 138/udp

ENTRYPOINT ["/entrypoint.sh"]
