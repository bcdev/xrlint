import contextlib
from typing import Any, Literal

import xarray as xr

from xrlint.config import Config
from xrlint.constants import MISSING_FILE_PATH
from xrlint.constants import SEVERITY_ERROR
from xrlint.node import Node
from xrlint.message import Message
from xrlint.message import Suggestion
from xrlint.rule import RuleContext


class RuleContextImpl(RuleContext):
    def __init__(
        self,
        config: Config,
        *,
        dataset: xr.Dataset | None,
        file_path: str | None,
    ):
        assert not (dataset is None and file_path is None)
        self._config = config
        self._dataset = dataset
        self._file_path = self._get_file_path(file_path, dataset)
        self.messages: list[Message] = []
        self.rule_id: str | None = None
        self.severity: Literal[1, 2] = SEVERITY_ERROR
        self.node: Node | None = None

    @property
    def settings(self) -> dict[str, Any]:
        assert self._config is not None
        return self._config.settings or {}

    @property
    def dataset(self) -> xr.Dataset:
        # self._dataset may be None, e.g., if it could not be opened.
        # But in this case we never should enter user code, hence,
        # we will see the assertion error only in our own code.
        assert self._dataset is not None
        return self._dataset

    @property
    def file_path(self) -> str:
        assert self._file_path is not None
        return self._file_path

    def report(
        self,
        message: str,
        *,
        fatal: bool | None = None,
        suggestions: list[Suggestion] | None = None,
    ):
        m = Message(
            message=message,
            fatal=fatal,
            suggestions=suggestions,
            rule_id=self.rule_id,
            node_path=self.node.path if self.node is not None else None,
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

    @staticmethod
    def _get_file_path(file_path: str | None, dataset: xr.Dataset | None) -> str:
        if not file_path:
            if dataset is not None:
                file_path = dataset.encoding.get("source")
                if isinstance(file_path, str):
                    file_path = file_path
            if not file_path:
                file_path = MISSING_FILE_PATH
        return file_path
