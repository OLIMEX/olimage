import jinja2
import logging
import os
import re



logger = logging.getLogger(__name__)


class Template(object):
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

        # If files is not a list, convert it to such
        if not isinstance(files, list):
            files = [files]

        for file in files:
            logger.debug("Generating template file : {}".format(file))
            with open(file, 'r') as f:
                data = f.read()

            # Render template
            template = jinja2.Template(data, trim_blocks=True, keep_trailing_newline=False)
            data = template.render(**kwargs)
            with open(file, 'w') as f:
                f.write(data + "\n")

            # Set file permissions
            if permissions is not None:
                if re.match("^[0-7]{3}$", permissions) is None:
                    raise ValueError("Invalid permissions string: {}".format(permissions))
                os.chmod(file, int("0o" + permissions, 8))