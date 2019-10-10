from .config import GenericConfig


class Images(GenericConfig):
    """
    Parse available images
    """
    config = "images"

    def get_packages(self, variant):

        def unpack(l):
            r = []
            for item in l:
                if type(item) != list:
                    r.append(item)
                    continue
                else:
                    r += unpack(item)

            return r

        for v in self:
            if str(v) == variant:
                return unpack(v.packages)


