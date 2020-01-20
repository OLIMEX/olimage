u-boot-olinuxino
================

About
-----

The suggested way of building the package is using docker.


Prepare
-------

See additional documentation about the used image here:
https://hub.docker.com/r/multiarch/qemu-user-static/

Register **binfmt_misc**:

.. code-block:: bash

    docker run --rm --privileged multiarch/qemu-user-static:register --reset

Create a new Dockerfile:

.. code-block:: docker

    FROM multiarch/debian-debootstrap:arm64-sid

    ENV DEBIAN_FRONTEND noninteractive

    RUN apt-get update && \
        apt-get install -y --no-install-recommends \
            bc \
            bison \
            build-essential \
            debhelper-compat \
            device-tree-compiler \
            devscripts \
            flex \
            git \
            git-buildpackage \
            libfdt-dev \
            libpython3-dev \
            python3 \
            python3-distutils \
            swig && \
        rm -rf /var/lib/apt/lists/*

**Note**: In the example arm64 architecture is used. To use armhf
change

.. code-block:: docker

    FROM multiarch/debian-debootstrap:arm64-sid

to

.. code-block:: docker

    FROM multiarch/debian-debootstrap:armhf-sid

Build the new image:

.. code-block:: bash

    docker build . -t u-boot-olinuxino


Build package
-------------

.. code-block:: bash

    mkdir u-boot
    cd u-boot
    git clone https://github.com/olimage/u-boot-olinuxino.git
    docker run --rm -it -v $(pwd):/u-boot -w /u-boot/u-boot-olinuxino u-boot-olinuxino gbp buildpackage --git-upstream-tree=v2020.01 --git-builder='debuild --no-lintian -i -I'


**Note**: Here the latest used release is **v2020.01**. In the future this may change.