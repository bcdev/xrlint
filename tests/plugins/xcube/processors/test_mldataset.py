#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

import json
from typing import Any
from unittest import TestCase

import fsspec
import pytest
import xarray as xr

from tests.plugins.xcube.helpers import make_cube_levels
from xrlint.plugins.xcube.constants import ML_INFO_ATTR
from xrlint.plugins.xcube.processors.mldataset import MultiLevelDatasetProcessor
from xrlint.plugins.xcube.util import LevelInfo, LevelsMeta
from xrlint.result import Message

# TODO: This tests requires zarr >=2, <3, because the test used fsspec's
#   memory filesystem, which is not async but zarr wants all filesystems
#   to be async now.


class MultiLevelDatasetProcessorTest(TestCase):
    levels_name = "xrlint-test"
    levels_dir = f"memory://{levels_name}.levels"

    x_size = nx = 720
    y_size = ny = 360
    time_size = 3
    num_levels = 4

    meta_path = f"{levels_dir}/.zlevels"
    meta_content = {
        "version": "1.0",
        "num_levels": num_levels,
        "use_saved_levels": False,
        # tile_size is optional
        "agg_methods": {
            "chl": "mean",
        },
    }

    @classmethod
    def setUpClass(cls):
        fs, _ = fsspec.core.url_to_fs(cls.levels_dir)
        cls.fs: fsspec.AbstractFileSystem = fs

    def setUp(self):
        self._delete_files()
        self.fs.mkdir(self.levels_dir)

        level_datasets = make_cube_levels(
            self.num_levels, self.x_size, self.y_size, self.time_size
        )
        for level, dataset in enumerate(level_datasets):
            dataset.to_zarr(f"{self.levels_dir}/{level}.zarr")

        with self.fs.open(self.meta_path, mode="wt") as stream:
            json.dump(self.meta_content, stream, indent=2)

    def tearDown(self):
        self._delete_files()

    def _delete_files(self):
        if self.fs.exists(self.levels_dir):
            self.fs.delete(self.levels_dir, recursive=True)

    def assert_levels_ok(
        self, datasets: Any, expect_meta: bool = False, expect_link: bool = False
    ):
        self.assertIsInstance(datasets, list)
        self.assertEqual(self.num_levels, len(datasets))
        for i, (dataset, file_path) in enumerate(datasets):
            if expect_link and i == 0:
                self.assertEqual(f"memory://{self.levels_name}.zarr", file_path)
            else:
                self.assertEqual(
                    f"memory://{self.levels_name}.levels/{i}.zarr", file_path
                )
            level_info = dataset.attrs.get(ML_INFO_ATTR)
            self.assertIsInstance(level_info, LevelInfo)
            self.assertEqual(i, level_info.level)
            self.assertEqual(self.num_levels, level_info.num_levels)
            self.assertIsInstance(level_info.datasets, list)
            self.assertEqual(self.num_levels, len(level_info.datasets))
            meta = level_info.meta
            if expect_meta:
                self.assertIsInstance(meta, LevelsMeta)
                self.assertEqual("1.0", meta.version)
                self.assertEqual(self.num_levels, meta.num_levels)
                self.assertEqual(False, meta.use_saved_levels)
                self.assertEqual(None, meta.tile_size)
                self.assertEqual({"chl": "mean"}, meta.agg_methods)
            else:
                self.assertIsNone(meta)

    def preprocess(self) -> list[tuple[xr.Dataset, str]]:
        processor = MultiLevelDatasetProcessor()
        return processor.preprocess(self.levels_dir, {})

    def test_preprocess(self):
        datasets = self.preprocess()
        self.assert_levels_ok(datasets, expect_meta=True)

    def test_preprocess_no_meta(self):
        self.fs.delete(self.meta_path)
        datasets = self.preprocess()
        self.assert_levels_ok(datasets, expect_meta=False)

    def test_preprocess_with_link(self):
        self.fs.copy(
            f"{self.levels_dir}/0.zarr",
            f"memory://{self.levels_name}.zarr",
            recursive=True,
        )
        self.fs.delete(f"{self.levels_dir}/0.zarr", recursive=True)
        self.fs.write_text(f"{self.levels_dir}/0.link", f"../{self.levels_name}.zarr")
        datasets = self.preprocess()
        self.assert_levels_ok(datasets, expect_meta=True, expect_link=True)

    def test_preprocess_fail_empty(self):
        for i in range(self.num_levels):
            self.fs.delete(f"{self.levels_dir}/{i}.zarr", recursive=True)
        with pytest.raises(ValueError, match="empty multi-level dataset"):
            self.preprocess()

    def test_preprocess_fail_missing(self):
        self.fs.delete(f"{self.levels_dir}/1.zarr", recursive=True)
        with pytest.raises(
            ValueError, match="missing dataset for level 1 in multi-level dataset"
        ):
            self.preprocess()

    def test_postprocess(self):
        processor = MultiLevelDatasetProcessor()
        ml0 = [Message("m00"), Message("m01")]
        ml1 = [Message("10"), Message("m11"), Message("m12")]
        messages = processor.postprocess(
            [
                ml0,
                ml1,
            ],
            self.levels_dir,
        )
        self.assertEqual([*ml0, *ml1], messages)
