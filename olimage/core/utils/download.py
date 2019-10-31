import git
import logging
import os
import shutil

logger = logging.getLogger(__name__)


class Download(object):

    @staticmethod
    def git(url: str, path: str, ref='master') -> str:
        """
        Perform git clone

        :param url: Remote sources URL
        :param path: Destination path
        :param ref: branch/tag for checkout
        :return: repo directory
        """
        logger.info("Cloning {} from {} to {}".format(ref, url, path))

        # The actual dl path is <package>/<refs>
        dl = os.path.join(path, ref)

        # Remove directory is already exists
        shutil.rmtree(dl, ignore_errors=True)

        # Clone the repo
        repo = git.Repo.clone_from(url, dl, depth=1, branch=ref)

        return repo.working_dir
