import json
from unittest import TestCase

import fsspec

from tests.plugins.xcube.helpers import make_cube
from xrlint.plugins.xcube.processors.mldataset import MultiLevelDatasetProcessor
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
            self.assertIn("_LEVEL_INFO", dataset.attrs)
            level_info = dataset.attrs.get("_LEVEL_INFO")
            self.assertIsInstance(level_info, dict)
            self.assertEqual(i, level_info.get("index"))
            self.assertEqual(self.nl, level_info.get("count"))
            self.assertEqual(self.meta_path, level_info.get("meta_path"))
            self.assertEqual(self.meta_content, level_info.get("meta_content"))
            self.assertIsInstance(level_info.get("datasets"), list)

        self.fs.delete(self.meta_path)

    def test_preprocess_no_meta(self):
        processor = MultiLevelDatasetProcessor()
        datasets = processor.preprocess(self.levels_dir, {})
        self.assertIsInstance(datasets, list)
        self.assertEqual(self.nl, len(datasets))
        for i, (dataset, file_path) in enumerate(datasets):
            self.assertEqual(f"{self.levels_dir}/{i}.zarr", file_path)
            self.assertIn("_LEVEL_INFO", dataset.attrs)
            level_info = dataset.attrs.get("_LEVEL_INFO")
            self.assertIsInstance(level_info, dict)
            self.assertEqual(i, level_info.get("index"))
            self.assertEqual(self.nl, level_info.get("count"))
            self.assertEqual(None, level_info.get("meta_path"))
            self.assertEqual(None, level_info.get("meta_content"))
            self.assertIsInstance(level_info.get("datasets"), list)

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
