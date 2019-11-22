import olimage.environment as env

from .shell import Shell as shell


class Install(object):
    @staticmethod
    def __call__(files, mode='644'):
        if not isinstance(files, list):
            files = [files]

        for file in files:
            source = env.paths['overlay'] + file
            destination = env.paths['debootstrap'] + file

            shell.run('install -D -v -m {} {} {}'.format(mode, source, destination))