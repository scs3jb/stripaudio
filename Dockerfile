FROM phusion/baseimage:0.9.15
MAINTAINER scs3jb <scs3jb@nope>
ENV DEBIAN_FRONTEND noninteractive

RUN /etc/my_init.d/00_regen_ssh_host_keys.sh

RUN usermod -u 99 nobody
RUN usermod -g 100 nobody

VOLUME /cache
VOLUME /array

RUN apt-get update \
    && apt-get install -y mkvtoolnix python libav-tools \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*


ADD original.py /opt/original.py
RUN chmod +x /opt/original.py
