FROM debian:latest

# Define arguments
ARG USER
ARG GID
ARG UID

# Install packages
RUN apt-get update
RUN apt-get install -y \
    bc \
    bison \
    cpio \
    debootstrap \
    device-tree-compiler \
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
    sudo \
    swig \
    qemu-user-static \
    qemu-utils \
    quilt \
    u-boot-tools \
    udev

# Install pip packages
RUN pip3 install \
    click \
    GitPython \
    halo \
    jinja2 \
    pykwalify \
    pinject \
    pyyaml

RUN pip3 install http://deb.debian.org/debian/pool/main/p/python-cliapp/python-cliapp_1.20180812.1.orig.tar.xz

# Generate home directory for the current user
WORKDIR /home/${USER}

# Generate ~/.quiltrc file
RUN echo '\
QUILT_NO_DIFF_INDEX=1\n\
QUILT_NO_DIFF_TIMESTAMPS=1\n\
QUILT_REFRESH_ARGS="-p ab"\n\
QUILT_DIFF_ARGS="-p ab --color=auto"\n\
QUILT_PATCH_OPTS="--reject-format=unified"\n\
QUILT_COLORS="diff_hdr=1;32:diff_add=1;34:diff_rem=1;31:diff_hunk=1;33:diff_ctx=35:diff_cctx=33"\n'\
>> /home/${USER}/.quiltrc

# Fix permissions
RUN chown -R ${UID}:${GID} /home/${USER}

# Allow sudo without password
RUN echo "${USER} ALL=(root) NOPASSWD:ALL" > /etc/sudoers.d/${USER} && \
    chmod 0440 /etc/sudoers.d/${USER}

ENTRYPOINT ["/bin/bash"]