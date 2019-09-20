import functools
import datetime
import subprocess
import sys
import time

import halo


class Printer(halo.Halo):
    """Wrapper for halo module"""

    def __call__(self, f):
        """Allow the Halo object to be used as a regular function decorator."""

        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            with self:
                line = self.text
                args[0].printer = self
                try:
                    start = time.time()
                    ret = f(*args, **kwargs)

                    self.text = self.text + ' : {} '.format(str(datetime.timedelta(seconds=int(time.time() - start))))
                    self.succeed()
                    return ret

                except Exception as e:
                    self.fail()
                    print("    {}".format(e))
                    raise e

                finally:
                    self.text = line

        return wrapped
