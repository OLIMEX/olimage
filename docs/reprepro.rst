Local debian repository
=======================

About
-----

You can use a local debian repository for testing (or not). This
is done by using reprepro + nginx.

The mountpoints are:

* **/var/reprepro/debian** - the repository base directory

Include a new package
---------------------

Copy all files to *docker/reprepro/data/packages*.

Attach to the running reprepro container:

.. code-block:: bash

    docker exec -it docker_reprepro_1 /bin/bash

Include package the with:

.. code-block:: bash

    cd /data/packages
    reprepro include <release> <package>.changes



