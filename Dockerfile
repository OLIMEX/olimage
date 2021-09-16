FROM ubuntu:focal

ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

ENV DEBIAN_FRONTEND noninteractive

# Install packages
RUN apt-get update && \
    apt-get install -y \
        debootstrap \
        gdisk \
        kpartx \
        parted \
        python-dev \
        python3 \
        python3-gdbm \
        python3-pip \
        python3-tk \
        python3-cerberus \
        python3-click \
        python3-jinja2 \
        python3-yaml \
        python3-cliapp \
        rsync \
        qemu-user-static \
        qemu-utils \
        u-boot-tools \
        udev && \
    rm -rf /var/lib/apt/lists/*

# Install pip packages
RUN pip3 install \
    halo \
    pinject
