FROM debian:latest

ENV DEBIAN_FRONTEND noninteractive

# Install packages
RUN apt-get update && \
    apt-get install -y \
        debootstrap \
        kpartx \
        parted \
        python-dev \
        python3 \
        python3-gdbm \
        python3-pip \
        python3-tk \
        rsync \
        qemu-user-static \
        qemu-utils \
        u-boot-tools \
        udev && \
    rm -rf /var/lib/apt/lists/*

# Install pip packages
RUN pip3 install \
    cerberus \
    click \
    halo \
    jinja2 \
    pinject \
    pyyaml

RUN pip3 install http://deb.debian.org/debian/pool/main/p/python-cliapp/python-cliapp_1.20180812.1.orig.tar.xz