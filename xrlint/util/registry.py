from collections.abc import Mapping, dict_items
from typing import Generic, TypeVar, Iterator

RegistryItem = TypeVar("RegistryItem")


class Registry(Generic[RegistryItem], Mapping[str, RegistryItem]):

    def __init__(self):
        self._items: dict[str, RegistryItem] = {}

    def __getitem__(self, key: str, /):
        return self._items[key]

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self):
        return iter(self._items)

    def items(self):
        return self._items.items()

    def as_dict(self) -> dict[str, RegistryItem]:
        return dict(self._items)

    def register(self, name: str, item: RegistryItem):
        # warn if exists?
        self._items[name] = item

    def lookup(self, name: str) -> RegistryItem | None:
        return self._items.get(name)
