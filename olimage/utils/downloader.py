import logging
import os
import shutil

import git
from git.exc import CommandError, InvalidGitRepositoryError, RepositoryDirtyError, GitCommandError

from olimage.utils.printer import Printer
from olimage.utils.stamper import PackageStamper
from olimage.utils import Util

logger = logging.getLogger(__name__)


class Downloader(Util):

    def __init__(self, name, config):

        # Initialize parent
        super().__init__(name, config)

        # Configure stamper
        self._stamper = PackageStamper(self.paths['package'])

    @property
    def printer(self):
        return self._printer

    @printer.setter
    def printer(self, printer):
        self._printer = printer

    def download(self):
        # Check existing stamps
        stamps = self._stamper.stamps

        if 'downloaded' not in stamps:
            if os.path.exists(self.paths['clone']):
                logger.debug("Removing {} existing folder".format(self.paths['clone']))
                shutil.rmtree(self.paths['clone'])

            repo = self.clone()
            self._stamper.stamp('downloaded')

            return self.archive(repo)

        else:
            try:
                logger.debug("Checking repository: {}".format(self.paths['clone']))
                repo = git.Repo(self.paths['clone'])

                if repo.is_dirty(untracked_files=True):
                    raise RepositoryDirtyError(repo, None)

                if 'archived' in self._stamper.stamps:
                    return repo

                return self.archive(repo)

            except InvalidGitRepositoryError:
                logger.error("Folder \'{}\' is not a valid git repository. Removing.".format(self.paths['clone']))
            except RepositoryDirtyError:
                logger.error("Repository \'{}\' is dirty. Removing.".format(self.paths['clone']))

            if self._try_count > 5:
                raise Exception("Failed to clone {}".format(self.config['source']))
            self._try_count += 1

            # Remove package download folder and try again
            shutil.rmtree(self.paths['package'])
            os.mkdir(self.paths['package'])
            return Downloader.download()

    @Printer("Cloning repository")
    def clone(self):

        self._printer.text += " \'{} {}\'".format(self._config['source'], self._config['refs'])
        logger.info("Cloning {} from {} to {}".format(self._config['refs'], self._config['source'], self.paths['clone']))

        return git.Repo.clone_from(self._config['source'], self.paths['clone'], depth=1, branch=self._config['refs'])

    @Printer("Archiving repository")
    def archive(self, repo):

        self.printer.text += " \'{}\'".format(os.path.basename(self.paths['archive']))
        logger.info("Creating archive {}".format(os.path.basename(self.paths['archive'])))

        with open(self.paths['archive'], 'wb') as f:
            repo.archive(f, format='tar.gz')

        self._stamper.stamp('archived')
        return repo





