import olimage.environment as env

from olimage.core.io import Console
from olimage.core.parsers import (Repository, Repositories)
from olimage.core.utils import Utils

from .base import SetupAbstract


class SetupApt(SetupAbstract):

    def setup(self, release: str):

        with Console("Installing packages"):
            Utils.shell.chroot('apt-get install -y {}'.format(' '.join(self.packages)))

        for repo in Repositories():
            repo: Repository

            if repo.testing and env.options['releaseimage']:
                continue

            with Console("Adding: \'{}\'".format(repo.url)):
                file = '/etc/apt/sources.list.d/{}.list'.format(str(repo))

                source = env.paths['overlay'] + '/etc/apt/sources.list.d/default.list'
                destination = env.paths['build'] + file

                # # Install source list
                Utils.shell.run("install -m 644 {} {}".format(source, destination))
                Utils.template.install(destination, repo=repo, release=release)

                if repo.key and repo.keyserver:
                    # Import gpg key
                    Utils.shell.chroot('apt-key adv --keyserver {} --recv-keys {}'.format(repo.keyserver, repo.key))

                elif repo.keyfile:
                    # Import keyfile
                    Utils.install(repo.keyfile)
                    Utils.shell.chroot('apt-key add {}'.format(repo.keyfile))

        # Update sources
        # It's possible for some repository to have missing release files, so
        # for now ignore error upon update
        with Console("Updating"):
            Utils.shell.chroot('apt-get update', ignore_fail=True)
