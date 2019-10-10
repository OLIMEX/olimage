import logging
import os
import shutil

import git
from git.exc import InvalidGitRepositoryError, RepositoryDirtyError, NoSuchPathError


from .stamper import PackageStamper
from .util import Util

logger = logging.getLogger(__name__)


class Downloader(Util):

    def __init__(self, name, config):

        # Initialize parent
        super().__init__(name, config)

        # Configure stamper
        self._stamper = PackageStamper(self.paths['package'])

        self._try_count = 0

    def download(self):

        # Check existing stamps
        stamps = self._stamper.stamps

        if 'downloaded' not in stamps:
            if os.path.exists(self.paths['clone']):
                logger.debug("Removing {} existing folder".format(self.paths['clone']))
                shutil.rmtree(self.paths['clone'])

            if os.path.exists(self.paths['build']):
                logger.debug("Removing {} existing folder".format(self.paths['build']))
                shutil.rmtree(self.paths['build'])

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
            except NoSuchPathError:
                logger.error("Possibly changed refs. Cleaning-up.")

            if self._try_count > 5:
                raise Exception("Failed to clone {}".format(self.config['source']))
            self._try_count += 1

            # Remove package download folder and try again
            shutil.rmtree(self.paths['package'])
            os.mkdir(self.paths['package'])
            return self.download()

    def clone(self):

        logger.info("Cloning {} from {} to {}".format(self._config['refs'], self._config['source'], self.paths['clone']))
        return git.Repo.clone_from(self._config['source'], self.paths['clone'], depth=1, branch=self._config['refs'])

    def archive(self, repo):

        logger.info("Creating archive {}".format(os.path.basename(self.paths['archive'])))

        with open(self.paths['archive'], 'wb') as f:
            repo.archive(f, format='tar.gz')

        self._stamper.stamp('archived')
        return repo





