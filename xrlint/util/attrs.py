#  Copyright © 2026 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

from collections.abc import Iterator, Mapping
from typing import Any

from xrlint.node import DatasetNode, DataTreeNode


class HierarchicalAttrs(Mapping[str, Any]):
    """Attribute lookup for metadata rules with DataTree parent context."""

    def __init__(self, node: DatasetNode):
        self._attrs_by_precedence = [node.dataset.attrs]
        parent = node.parent
        while isinstance(parent, DataTreeNode):
            self._attrs_by_precedence.append(parent.datatree.attrs)
            parent = parent.parent

    def __contains__(self, key: object) -> bool:
        return any(key in attrs for attrs in self._attrs_by_precedence)

    def __getitem__(self, key: str) -> Any:
        for attrs in self._attrs_by_precedence:
            if key in attrs:
                return attrs[key]
        raise KeyError(key)

    def __iter__(self) -> Iterator[str]:
        seen: set[str] = set()
        for attrs in self._attrs_by_precedence:
            for key in attrs:
                if key not in seen:
                    seen.add(key)
                    yield key

    def __len__(self) -> int:
        return sum(1 for _ in self)


def hierarchical_attrs(node: DatasetNode) -> HierarchicalAttrs:
    return HierarchicalAttrs(node)
