import logging

from .shell import Shell


logger = logging.getLogger(__name__)


class Qemu(object):

    @staticmethod
    def debootstrap(arch, release, path, components=None, include=None, mirror=None):
        logger.info("Running qemu-debootstrap")
        Shell.run(
            "qemu-debootstrap --arch={} {} {} {} {} {}".format(
                arch,
                "" if components is None else "--components=" + ",".join(components),
                "" if include is None else "--include=" + ",".join(include),
                release, path,
                "" if mirror is None else mirror),
            logger
        )

    @staticmethod
    def img(file, size):
        logger.info("Creating {}".format(file))
        Shell.run(
            "qemu-img create -f raw {} {}M".format(file, size),
            logger
        )
