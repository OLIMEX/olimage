from olimage.rootfs.filesystem import FileSystemBase


class FileSystemBase(FileSystemBase):
    variant = 'base'

    def build(self):
        pass

    def configure(self):
        pass

    def cleanup(self):
        pass