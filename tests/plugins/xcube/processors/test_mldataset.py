import json
from unittest import TestCase

import fsspec

from tests.plugins.xcube.helpers import make_cube
from xrlint.plugins.xcube.constants import ML_INFO_ATTR
from xrlint.plugins.xcube.processors.mldataset import (
    MultiLevelDatasetProcessor,
    LevelInfo,
    MultiLevelDatasetMeta,
)
from xrlint.result import Message


class MultiLevelDatasetProcessorTest(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.levels_dir = "memory://xrlint-test.levels"
        cls.fs, _ = fsspec.core.url_to_fs(cls.levels_dir)
        cls.fs.mkdir(cls.levels_dir)

        cls.nx = nx = 720
        cls.ny = ny = nx // 2
        cls.nt = 3
        cls.nl = 4

        for level in range(cls.nl):
            dataset = make_cube(nx, ny, cls.nt)
            dataset.to_zarr(f"{cls.levels_dir}/{level}.zarr", write_empty_chunks=False)
            nx //= 2
            ny //= 2

        cls.meta_path = f"{cls.levels_dir}/.zlevels"
        cls.meta_content = {
            "version": "1.0",
            "num_levels": cls.nl,
            "use_saved_levels": False,
            "agg_methods": {
                "chl": "mean",
            },
        }

    def test_preprocess(self):
        with self.fs.open(self.meta_path, mode="wt") as stream:
            json.dump(self.meta_content, stream, indent=2)

        processor = MultiLevelDatasetProcessor()
        datasets = processor.preprocess(self.levels_dir, {})
        self.assertIsInstance(datasets, list)
        self.assertEqual(self.nl, len(datasets))
        for i, (dataset, file_path) in enumerate(datasets):
            self.assertEqual(f"{self.levels_dir}/{i}.zarr", file_path)
            level_info = dataset.attrs.get(ML_INFO_ATTR)
            self.assertIsInstance(level_info, LevelInfo)
            self.assertEqual(i, level_info.level)
            self.assertEqual(self.nl, level_info.num_levels)
            self.assertIsInstance(level_info.meta, MultiLevelDatasetMeta)
            self.assertIsInstance(level_info.datasets, list)
            self.assertEqual(self.nl, len(level_info.datasets))

        self.fs.delete(self.meta_path)

    def test_preprocess_no_meta(self):
        processor = MultiLevelDatasetProcessor()
        datasets = processor.preprocess(self.levels_dir, {})
        self.assertIsInstance(datasets, list)
        self.assertEqual(self.nl, len(datasets))
        for i, (dataset, file_path) in enumerate(datasets):
            self.assertEqual(f"{self.levels_dir}/{i}.zarr", file_path)
            level_info = dataset.attrs.get(ML_INFO_ATTR)
            self.assertIsInstance(level_info, LevelInfo)
            self.assertEqual(i, level_info.level)
            self.assertEqual(self.nl, level_info.num_levels)
            self.assertEqual(None, level_info.meta)
            self.assertIsInstance(level_info.datasets, list)
            self.assertEqual(self.nl, len(level_info.datasets))

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
