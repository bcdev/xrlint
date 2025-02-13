#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

from abc import ABC
from dataclasses import dataclass
from typing import Any, Hashable, Union

import xarray as xr


@dataclass(frozen=True, kw_only=True)
class Node(ABC):
    """Abstract base class for nodes passed to the methods of a
    rule operation [xrlint.rule.RuleOp][]."""

    path: str
    """Node path. So users find where in the tree the issue occurred."""

    parent: Union["Node", None]
    """Node parent. `None` for root nodes."""


@dataclass(frozen=True, kw_only=True)
class XarrayNode(Node):
    """Base class for `xr.Dataset` nodes."""

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
class DataTreeNode(XarrayNode):
    """DataTree node."""

    name: Hashable
    """The name of the datatree."""

    datatree: xr.DataTree
    """The `xarray.DataTree` instance."""


@dataclass(frozen=True, kw_only=True)
class DatasetNode(XarrayNode):
    """Dataset node."""

    name: Hashable
    """The name of the dataset."""

    dataset: xr.Dataset
    """The `xarray.Dataset` instance."""


@dataclass(frozen=True, kw_only=True)
class VariableNode(XarrayNode):
    """Variable node.
    Could be a coordinate or data variable.
    If you need to distinguish, you can use expression
    `node.name in ctx.dataset.coords`.
    """

    name: Hashable
    """The name of the variable."""

    array: xr.DataArray
    """The `xarray.DataArray` instance."""


@dataclass(frozen=True, kw_only=True)
class AttrsNode(XarrayNode):
    """Attributes node."""

    attrs: dict[str, Any]
    """Attributes dictionary."""


@dataclass(frozen=True, kw_only=True)
class AttrNode(XarrayNode):
    """Attribute node."""

    name: str
    """Attribute name."""

    value: Any
    """Attribute value."""
