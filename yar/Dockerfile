#
# Use the latest ubuntu, which is currently 20.04
#
# Testing with upgrade to last-known-good
FROM ubuntu:24.04
MAINTAINER 48clyde
ENV DEBIAN_FRONTEND=noninteractive

#
# Get the required extras and clean up
#
RUN apt-get update -y && \
  apt-get install -qy abcde cdparanoia eject flac netcat-openbsd setcd sdparm eyed3 lame cd-discid && \
  apt-get remove -qy postfix && \
  apt-get -qy clean && \
  apt-get -qy purge && \
  apt-get -qy autoremove && \
  rm -rf /var/lib/apt/lists/*

#
# copy into the container the custom conf and the main
# shell script that checks for disks having been inserted
#
COPY abcde-local.conf /etc/abcde-local.conf
COPY yar.sh /usr/local/bin/yar.sh

ENTRYPOINT ["/usr/local/bin/yar.sh"]
