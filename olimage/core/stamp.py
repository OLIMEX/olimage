import functools
import logging
import os

import olimage.environment as env

logger = logging.getLogger(__name__)


def stamp(func):

    @functools.wraps(func)
    def wrapper(*args, **kwargs):

        file = os.path.join(env.paths['debootstrap'], '.stamp_' + func.__name__.lstrip('_'))

        # Check if stamp exists
        if os.path.isfile(file):
            logger.debug("Found existing stamp: {}. Skipping".format(file))
            return

        # Run function
        ret = func(*args, **kwargs)

        # Stamp
        logger.debug("Creating stamp: {}".format(file))
        open(file, 'x').close()

        return ret

    return wrapper