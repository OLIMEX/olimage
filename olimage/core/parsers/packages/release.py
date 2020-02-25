from .base import PackagesBase


class Release(PackagesBase):
    def get_variant(self, variant: str) -> list:
        if variant not in self._data:
            return []

        return self._data[variant]
