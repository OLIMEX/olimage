import os

import olimage.environment as env

from olimage.core.parsers import (Repository, Repositories)
from olimage.core.printer import Print
from olimage.core.utils import Utils


class Apt(object):

    @staticmethod
    @Print.process("APT repositories")
    def __call__(release: str):

        # Install gnupg
        Utils.shell.chroot('apt-get install -y gnupg')

        for repo in Repositories():
            repo: Repository

            file = '/etc/apt/sources.list.d/{}.list'.format(str(repo))

            source = env.paths['overlay'] + '/etc/apt/sources.list.d/default.list'
            destination = env.paths['debootstrap'] + file

            # # Install source list
            Utils.shell.run("install -m 644 {} {}".format(source, destination))
            Utils.template.install(destination, repo=repo, release=release)

            if repo.key and repo.keyserver:
                # Import gpg key
                Utils.shell.chroot('apt-key adv --keyserver {} --recv-keys {}'.format(repo.keyserver, repo.key))

        # Update sources
        Utils.shell.chroot('cat /etc/apt/sources.list.d/olimex.list')
        Utils.shell.chroot('apt-get update')

    @staticmethod
    def clean():
        Utils.shell.chroot('apt-get clean')

