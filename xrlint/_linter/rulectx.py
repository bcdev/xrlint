#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

import contextlib
from typing import Any, Literal

import xarray as xr

from xrlint.config import ConfigObject
from xrlint.constants import DATASET_ROOT_NAME, SEVERITY_ERROR
from xrlint.node import Node
from xrlint.result import Message, Suggestion
from xrlint.rule import RuleContext


class RuleContextImpl(RuleContext):
    def __init__(
        self,
        config: ConfigObject,
        dataset: xr.Dataset | xr.DataTree,
        file_path: str,
        file_index: int | None,
        access_latency: float | None,
    ):
        assert isinstance(config, ConfigObject)
        assert isinstance(dataset, (xr.Dataset | xr.DataTree))
        assert isinstance(file_path, str)
        assert file_index is None or isinstance(file_index, int)
        assert access_latency is None or isinstance(access_latency, float)
        if isinstance(dataset, xr.DataTree):
            datatree = dataset
            dataset = None
            if datatree.is_leaf:
                dataset = datatree.dataset
                datatree = None
        else:
            datatree = None
        self._config = config
        self._datatree = datatree
        self._dataset = dataset
        self._file_path = file_path
        self._file_index = file_index
        self._access_latency = access_latency
        self.messages: list[Message] = []
        self.rule_id: str | None = None
        self.severity: Literal[1, 2] = SEVERITY_ERROR
        self.node: Node | None = None

    @property
    def config(self) -> ConfigObject:
        return self._config

    @property
    def settings(self) -> dict[str, Any]:
        return self._config.settings or {}

    @property
    def datatree(self) -> xr.DataTree | None:
        return self._datatree

    @property
    def dataset(self) -> xr.Dataset | None:
        return self._dataset

    @dataset.setter
    def dataset(self, value: xr.Dataset) -> None:
        self._dataset = value

    @property
    def file_path(self) -> str:
        return self._file_path

    @property
    def file_index(self) -> int | None:
        return self._file_index

    @property
    def access_latency(self) -> float | None:
        return self._access_latency

    def report(
        self,
        message: str,
        *,
        fatal: bool | None = None,
        suggestions: list[Suggestion | str] | None = None,
    ):
        suggestions = (
            [Suggestion.from_value(s) for s in suggestions] if suggestions else None
        )
        m = Message(
            message=message,
            fatal=fatal,
            suggestions=suggestions,
            rule_id=self.rule_id,
            node_path=self.node.path if self.node is not None else DATASET_ROOT_NAME,
            severity=self.severity,
        )
        self.messages.append(m)

    @contextlib.contextmanager
    def use_state(self, **new_state):
        old_state = {k: getattr(self, k) for k in new_state.keys()}
        try:
            for k, v in new_state.items():
                setattr(self, k, v)
            yield
        finally:
            for k, v in old_state.items():
                setattr(self, k, v)
