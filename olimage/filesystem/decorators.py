import functools
import logging
import os
import shutil

import olimage.environment as env
from olimage.core.io import Console
from olimage.core.utils import Utils

from .base import FileSystemBase

logger = logging.getLogger()


def export(*args, **kwargs):
    if len(args) and callable(args[0]):
        func = args[0]

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Run function
            ret = func(*args, **kwargs)

            file = env.paths['build'] + '.' + func.__name__ + '.tar.gz'

            with Console("Creating archive: {}".format(os.path.basename(file))):
                Utils.archive.gzip(env.paths['build'], file,
                                   exclude=['/dev/*', '/proc/*', '/run/*', '/tmp/*', '/sys/*'])

            return ret

        return wrapper
    else:
        final = False
        if 'final' in kwargs and kwargs['final']:
            final = True
        def _wrapper(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # Run function
                ret = func(*args, **kwargs)

                if final:
                    file = env.paths['build'] + '.tar.gz'
                else:
                    file = env.paths['build'] + '.' + func.__name__ + '.tar.gz'

                with Console("Creating archive: {}".format(os.path.basename(file))):
                    Utils.archive.gzip(env.paths['build'], file,
                                       exclude=['/dev/*', '/proc/*', '/run/*', '/tmp/*', '/sys/*'])

                return ret

            return wrapper
        return _wrapper


def prepare(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        fs: FileSystemBase = args[0]

        # Create empty build folder
        if os.path.exists(fs.build_dir):
            # Make sure the target path is not mounted
            Utils.shell.unbind(fs.build_dir)
            shutil.rmtree(fs.build_dir)

        os.mkdir(fs.build_dir)

        stage = func.__name__
        index = fs.stages.index(stage)

        file = None

        # If this is the first stage, there is nothing to extract
        if index != 0:
            file = fs.build_dir + '.' + fs.stages[index - 1] + '.tar.gz'
        else:
            variants = ['minimal', 'base']
            _index = variants.index(fs.variant)

            if _index:
                file = fs.build_dir + '.tar.gz'
                file = file.replace(fs.variant, variants[_index -1])

        if file:
            with Console("Extracting archive: {}".format(os.path.basename(file))):
                Utils.archive.extract(file, fs.build_dir)

        return func(*args, **kwargs)

    return wrapper


def stamp(func):
    """
    Stamp filesystem creation. This should not be used outside of the filesystem command

    :param func: the wrapped function
    :return: the return value from the function
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):

        fs: FileSystemBase = args[0]

        # Check if the environment keys are set
        for key in ['filesystem', 'build']:
            if key not in env.paths:
                raise Exception("The path \'{}\' not set in the global environment".format(key))

        # Generate stamp for the exact filesystem: .stamp_<suite>-<variant>_<function>
        file = os.path.join(
            env.paths['filesystem'], '.stamp-' + os.path.basename(env.paths['build']) + '_' + func.__name__)

        # Check if stamp exists
        if os.path.isfile(file):
            logger.debug("Found existing stamp: {}. Skipping".format(file))
            return

        # Remove follow-up stamps
        stages = fs.stages
        for stage in stages:
            stages = stages[1:]
            if stage == func.__name__:
                break

        for stage in stages:
            path = os.path.join(env.paths['filesystem'], '.stamp_' + stage + '_' + os.path.basename(env.paths['build']))
            if os.path.isfile(path):
                logger.debug('Removing followup stamp: {}'.format(path))
                os.remove(path)

        # Run function
        ret = func(*args, **kwargs)

        # Stamp
        logger.debug("Creating stamp: {}".format(file))
        # TODO: Store hash sum for the directory. This way you can check for modifications
        # Probably with: tar -cf - somedir | md5sum
        open(file, 'x').close()

        return ret

    return wrapper



