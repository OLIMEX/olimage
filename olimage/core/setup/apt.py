import olimage.environment as env

from olimage.core.io import Console
from olimage.core.parsers import (Repository, Repositories)
from olimage.core.utils import Utils


class SetupApt(object):

    @staticmethod
    def __call__(release: str):

        with Console("Installing packages"):
            Utils.shell.chroot('apt-get install -y gnupg')

        for repo in Repositories():
            repo: Repository

            with Console("Installing repository: \'{}\'".format(repo.url)):
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
        # It's possible for some repository to have missing release files, so
        # for now ignore error upon update
        with Console("Updating sources list"):
            Utils.shell.chroot('apt-get update', ignore_fail=True)

    @staticmethod
    def clean():
        Utils.shell.chroot('apt-get clean')

