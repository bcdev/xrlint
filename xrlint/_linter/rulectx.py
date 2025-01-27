import contextlib
from typing import Any, Literal

import xarray as xr

from xrlint.config import Config
from xrlint.constants import NODE_ROOT_NAME, SEVERITY_ERROR
from xrlint.node import Node
from xrlint.result import Message, Suggestion
from xrlint.rule import RuleContext


class RuleContextImpl(RuleContext):
    def __init__(
        self,
        config: Config,
        dataset: xr.Dataset,
        file_path: str,
        file_index: int | None,
    ):
        assert config is not None
        assert dataset is not None
        assert file_path is not None
        assert file_index is None or isinstance(file_index, int)
        self._config = config
        self._dataset = dataset
        self._file_path = file_path
        self._file_index = file_index
        self.messages: list[Message] = []
        self.rule_id: str | None = None
        self.severity: Literal[1, 2] = SEVERITY_ERROR
        self.node: Node | None = None

    @property
    def config(self) -> Config:
        return self._config

    @property
    def settings(self) -> dict[str, Any]:
        return self._config.settings or {}

    @property
    def dataset(self) -> xr.Dataset:
        return self._dataset

    @property
    def file_path(self) -> str:
        return self._file_path

    @property
    def file_index(self) -> int | None:
        return self._file_index

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
            node_path=self.node.path if self.node is not None else NODE_ROOT_NAME,
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
