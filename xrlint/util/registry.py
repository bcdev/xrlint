from collections.abc import Mapping
from typing import Generic, TypeVar

T = TypeVar("T")


class Registry(Generic[T], Mapping[str, T]):
    def __init__(self):
        self._dict: dict[str, T] = {}

    def register(self, key: str, value: T):
        self._dict[key] = value

    def as_dict(self) -> dict[str, T]:
        return dict(self._dict)

    def get(self, key: str) -> T | None:
        return self._dict.get(key)

    def keys(self):
        return self._dict.keys()

    def values(self):
        return self._dict.values()

    def items(self):
        return self._dict.items()

    def __contains__(self, key: str):
        return key in self._dict

    def __getitem__(self, key: str):
        return self._dict[key]

    def __len__(self) -> int:
        return len(self._dict)

    def __iter__(self):
        return iter(self._dict)
