FROM debian:latest

RUN apt-get update

RUN apt-get install -y \
    bison \
    debootstrap \
    device-tree-compiler \
    dosfstools \
    gcc-aarch64-linux-gnu \
    git \
    flex \
    kpartx \
    parted \
    python-dev \
    python3 \
    python3-pip \
    rsync \
    swig \
    qemu-user-static \
    qemu-utils \
    udev

RUN pip3 install \
    click \
    GitPython \
    halo \
    jinja2 \
    pyyaml

RUN pip3 install http://git.liw.fi/cliapp/snapshot/cliapp-1.20180812.1.tar.gz

ENTRYPOINT ["/bin/bash"]