import logging
import os
import shutil

import git
from git.exc import CommandError, InvalidGitRepositoryError, RepositoryDirtyError, GitCommandError

from utils.printer import Printer
from utils.stamper import Stamper
from utils.package import Package

logger = logging.getLogger(__name__)


class Downloader(Package):

    def __init__(self, name, path, config):

        # Initialize parent
        super().__init__(name, path, config)

        # Configure stamper
        self._stamper = Stamper(self._path['package'])

    @property
    def printer(self):
        return self._printer

    @printer.setter
    def printer(self, printer):
        self._printer = printer

    def download(self):
        # Check existing stamps
        stamps = self._stamper.get_stamps()

        if 'downloaded' not in stamps:
            if os.path.exists(self._path['clone']):
                logger.debug("Removing {} existing folder".format(self._path['clone']))
                shutil.rmtree(self._path['clone'])

            repo = self.clone()
            self._stamper.stamp('downloaded')

            return self.archive(repo)

        else:
            try:
                logger.debug("Checking repository: {}".format(self._path['clone']))
                repo = git.Repo(self._path['clone'])

                if repo.is_dirty(untracked_files=True):
                    raise RepositoryDirtyError(repo, None)

                if 'archived' in self._stamper.get_stamps():
                    return repo

                return self.archive(repo)

            except InvalidGitRepositoryError:
                logger.error("Folder \'{}\' is not a valid git repository. Removing.".format(self._path['clone']))
            except RepositoryDirtyError:
                logger.error("Repository \'{}\' is dirty. Removing.".format(self._path['clone']))

            if self._try_count > 5:
                raise Exception("Failed to clone {}".format(self._config['source']))
            self._try_count += 1

            # Remove package download folder and try again
            shutil.rmtree(self._path['package'])
            os.mkdir(self._path['package'])
            return Downloader.download()

    @Printer("Cloning repository")
    def clone(self):

        self._printer.text += " \'{} {}\'".format(self._config['source'], self._config['refs'])
        logger.info("Cloning {} from {} to {}".format(self._config['refs'], self._config['source'], self._path['clone']))

        return git.Repo.clone_from(self._config['source'], self._path['clone'], depth=1, branch=self._config['refs'])

    @Printer("Archiving repository")
    def archive(self, repo):

        self.printer.text += " \'{}\'".format(os.path.basename(self._path['archive']))
        logger.info("Creating archive {}".format(os.path.basename(self._path['archive'])))

        with open(self._path['archive'], 'wb') as f:
            repo.archive(f, format='tar.gz')

        self._stamper.stamp('archived')
        return repo





