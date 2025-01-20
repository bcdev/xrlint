from typing import Any

import xarray as xr

from xrlint.plugins.xcube.plugin import plugin
from xrlint.processor import ProcessorOp
from xrlint.result import Message


@plugin.define_processor("multi-level-dataset")
class MultiLevelDatasetProcessor(ProcessorOp):
    """This processor should be used with `files: ["**/*.levels"]`."""

    def preprocess(
        self, file_path: str, opener_options: dict[str, Any]
    ) -> list[tuple[xr.Dataset, str]]:
        engine = opener_options.pop("engine", "zarr")
        new_file_path = file_path + "/" + "0.zarr"
        return [
            (
                xr.open_dataset(new_file_path, engine=engine, **opener_options),
                new_file_path,
            )
        ]

    def postprocess(
        self, messages: list[list[Message]], file_path: str
    ) -> list[Message]:
        return messages[0]
