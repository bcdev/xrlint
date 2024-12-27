from typing import Generic, TypeVar

RegistryItem = TypeVar("RegistryItem")


class Registry(Generic[RegistryItem]):
    def __init__(self):
        self._items: dict[str, RegistryItem] = {}

    def register(self, name: str, item: RegistryItem):
        # warn if exists?
        self._items[name] = item

    def lookup(self, name: str) -> RegistryItem | None:
        return self._items.get(name)

    def as_dict(self) -> dict[str, RegistryItem]:
        return dict(self._items)
