FROM debian:latest

RUN apt-get update

RUN apt-get install -y \
    debootstrap \
    dosfstools \
    kpartx \
    parted \
    python3 \
    python3-pip \
    rsync \
    qemu-user-static \
    qemu-utils \
    udev

RUN pip3 install \
    click \
    halo \
    jinja2 \
    pyyaml

RUN pip3 install http://git.liw.fi/cliapp/snapshot/cliapp-1.20180812.1.tar.gz

ENTRYPOINT ["/bin/bash"]