FROM debian:latest

ENV DEBIAN_FRONTEND noninteractive

# Install packages
RUN apt-get update && \
    apt-get install -y \
        bc \
        bison \
        cpio \
        debootstrap \
        device-tree-compiler \
        devscripts \
        dosfstools \
        gcc-aarch64-linux-gnu \
        git \
        flex \
        kmod \
        kpartx \
        libssl-dev \
        parted \
        python-dev \
        python3 \
        python3-pip \
        rsync \
        swig \
        qemu-user-static \
        qemu-utils \
        u-boot-tools \
        udev && \
    rm -rf /var/lib/apt/lists/*

# Install pip packages
RUN pip3 install \
    click \
    GitPython \
    halo \
    jinja2 \
    pinject \
    pyyaml

RUN pip3 install http://deb.debian.org/debian/pool/main/p/python-cliapp/python-cliapp_1.20180812.1.orig.tar.xz