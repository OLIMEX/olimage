import os

from .shell import Shell


class Patch(object):
    @staticmethod
    def quilt(patches, path):
        Shell.run(
            "cd {} && QUILT_PATCHES={} quilt push -a".format(path, patches),
            shell=True
        )

    @staticmethod
    def patch(file, path):
        Shell.run(
            "cd {} && patch -p1 < {}".format(path, file),
            shell=True
        )

    @staticmethod
    def apply(file, path):
        # Check if file is directory
        if os.path.isdir(file):
            # Check is 'series' file exists. If so use quilt, otherwise patch -p1
            if os.path.exists(os.path.join(file, 'series')):
                Patch.quilt(file, path)

            else:
                # Apply all .patch files
                for root, _, files in os.walk(file):
                    for file in sorted(files):
                        if file.endswith('.patch'):
                            Patch.patch(os.path.join(root, file), path)
