# Copyright (c) 2019 Olimex Ltd.
#
# MIT License
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import logging
import os

from jinja2 import Template

logger = logging.getLogger(__name__)


class Templater(object):
    """
    Install template files to target path
    """
    def __init__(self, source, target):
        """
        Configure paths

        :param source: Source directory
        :param target: Target directory
        """
        self._source = source
        self._target = target

    def install(self, files, **kwargs):
        """
        Render templates

        :param files: list with files, found in the source directory
        :param kwargs: kwargs passed to jinja2
        :return: self
        """
        logger.info("Installing template files: {}".format(files))

        for file in files:
            logger.debug("Generating template file : {}".format(file))
            with open(os.path.join(self._source, file), 'r') as f:
                data = f.read()

            tm = Template(data)
            data = tm.render(**kwargs)
            with open(os.path.join(self._target, file), 'w') as f:
                f.write(data + "\n")

        return self
