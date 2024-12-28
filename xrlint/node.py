from abc import ABC
from dataclasses import dataclass
from typing import Any, Hashable, Union

import xarray as xr


@dataclass(frozen=True, kw_only=True)
class Node(ABC):
    path: str
    parent: Union["Node", None]


@dataclass(frozen=True, kw_only=True)
class XarrayNode(Node):
    def in_coords(self) -> bool:
        """Return `True` if this node is in `xr.Dataset.coords`."""
        return ".coords[" in self.path

    def in_data_vars(self) -> bool:
        """Return `True` if this node is a `xr.Dataset.data_vars`."""
        return ".data_vars[" in self.path

    def in_root(self) -> bool:
        """Return `True` if this node is a direct child of the dataset."""
        return not self.in_coords() and not self.in_data_vars()


@dataclass(frozen=True, kw_only=True)
class AttrNode(XarrayNode):
    name: Any
    value: Any


@dataclass(frozen=True, kw_only=True)
class AttrsNode(XarrayNode):
    attrs: dict[str, Any]


@dataclass(frozen=True, kw_only=True)
class DataArrayNode(XarrayNode):
    name: Hashable
    data_array: xr.DataArray


@dataclass(frozen=True, kw_only=True)
class DatasetNode(XarrayNode):
    dataset: xr.Dataset
