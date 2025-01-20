import itertools
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

        level_datasets = []
        for level in itertools.count():
            level_path = f"{file_path}/{level}.zarr"
            try:
                level_dataset = xr.open_dataset(
                    level_path, engine=engine, **opener_options
                )
            except FileNotFoundError:
                break
            level_datasets.append((level_dataset, level_path))

        for level, (level_dataset, level_path) in enumerate(level_datasets):
            level_dataset.attrs["_LEVEL_INFO"] = {
                "index": level,
                "count": len(level_datasets),
                "datasets": [ds for ds, _ in level_datasets],
            }

        return level_datasets

    def postprocess(
        self, messages: list[list[Message]], file_path: str
    ) -> list[Message]:
        return list(itertools.chain(*messages))
