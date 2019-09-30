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
import re

from jinja2 import Template

logger = logging.getLogger(__name__)


class Templater(object):

    @staticmethod
    def install(files, permissions=None, **kwargs):
        """
        Render templates

        :param files: list with files, found in the source directory
        :param permissions: Set permissions upon write
        :param kwargs: kwargs passed to jinja2
        :return: self
        """
        logger.info("Installing template files: {}".format(files))

        for file in files:
            logger.debug("Generating template file : {}".format(file))
            with open(file, 'r') as f:
                data = f.read()

            tm = Template(data, trim_blocks=True, keep_trailing_newline=False)
            data = tm.render(**kwargs)
            with open(file, 'w') as f:
                f.write(data + "\n")

            if permissions is not None:
                if re.match("^[0-7]{3}$", permissions) is None:
                    raise ValueError("Invalid permissions string: {}".format(permissions))
                os.chmod(file, int("0o" + permissions, 8))
