from typing import Any
from unittest import TestCase

import pytest

from xrlint.config import Config, ConfigList, GlobalFilter


# noinspection PyMethodMayBeStatic
class ConfigTest(TestCase):
    def test_defaults(self):
        config = Config()
        self.assertEqual(None, config.name)
        self.assertEqual(None, config.files)
        self.assertEqual(None, config.ignores)
        self.assertEqual(None, config.linter_options)
        self.assertEqual(None, config.opener_options)
        self.assertEqual(None, config.processor)
        self.assertEqual(None, config.plugins)
        self.assertEqual(None, config.rules)

    def test_from_value_ok(self):
        self.assertEqual(Config(), Config.from_value(None))
        self.assertEqual(Config(), Config.from_value({}))
        self.assertEqual(Config(), Config.from_value(Config()))
        self.assertEqual(Config(name="x"), Config.from_value(Config(name="x")))
        self.assertEqual(
            Config(
                name="xXx",
                files=["**/*.zarr", "**/*.nc"],
                linter_options={"a": 4},
                opener_options={"b": 5},
                settings={"c": 6},
            ),
            Config.from_value(
                {
                    "name": "xXx",
                    "files": ["**/*.zarr", "**/*.nc"],
                    "linter_options": {"a": 4},  # not used yet
                    "opener_options": {"b": 5},  # not used yet
                    "settings": {"c": 6},
                }
            ),
        )

    def test_from_value_fails(self):
        with pytest.raises(
            TypeError, match="configuration must be of type dict, but was int"
        ):
            Config.from_value(4)
        with pytest.raises(
            TypeError, match="configuration must be of type dict, but was str"
        ):
            Config.from_value("abc")
        with pytest.raises(
            TypeError, match="configuration must be of type dict, but was tuple"
        ):
            Config.from_value(())
        with pytest.raises(
            TypeError,
            match="linter_options must be of type dict\\[str,Any\\], but was list",
        ):
            Config.from_value({"linter_options": [1, 2, 3]})
        with pytest.raises(
            TypeError, match="settings keys must be of type str, but was int"
        ):
            Config.from_value({"settings": {8: 9}})

    def test_global_filters_are_empty(self):
        files = ["**/*.zarr", "**/*.hdf"]
        ignores = ["**/*.tiff", "**/*.txt"]
        # empty
        self.assert_global_filters({"rules": {"r1": 2}}, (None, None))
        self.assert_global_filters({"settings": {"a": 17}}, (None, None))
        self.assert_global_filters({"files": files, "rules": {"r2": 0}}, (None, None))
        self.assert_global_filters(
            {"ignores": ignores, "settings": {"a": 19}}, (None, None)
        )
        # non-empty
        self.assert_global_filters({"files": None, "ignores": ignores}, (None, ignores))
        self.assert_global_filters({"files": [], "ignores": ignores}, (None, ignores))
        self.assert_global_filters({"files": files, "ignores": None}, (files, None))
        self.assert_global_filters({"files": files, "ignores": []}, (files, None))
        self.assert_global_filters(
            {"files": files, "ignores": ignores}, (files, ignores)
        )

    def assert_global_filters(self, config_obj: Any, expected_value: tuple):
        config = Config.from_value(config_obj)
        self.assertEqual(expected_value, config.global_filter_patterns)


class ConfigListTest(TestCase):
    def test_from_value(self):
        config_list = ConfigList.from_value([])
        self.assertIsInstance(config_list, ConfigList)
        self.assertEqual([], config_list.configs)

        config_list_2 = ConfigList.from_value(config_list)
        self.assertIs(config_list_2, config_list)

        config_list = ConfigList.from_value([{}])
        self.assertIsInstance(config_list, ConfigList)
        self.assertEqual([Config()], config_list.configs)

        with pytest.raises(
            TypeError,
            match=(
                "configuration list must be of type"
                " ConfigList|list\\[Config|dict\\], but was dict"
            ),
        ):
            ConfigList.from_value({})

    def test_compute_config(self):

        config_list = ConfigList([Config()])
        file_path = "s3://wq-services/datacubes/chl-2.zarr"
        self.assertEqual(
            Config(name="<computed>"), config_list.compute_config(file_path)
        )

        config_list = ConfigList(
            [
                Config(settings={"a": 1, "b": 1}),
                Config(files=["**/datacubes/*.zarr"], settings={"b": 2}),
                Config(files=["**/*.txt"], settings={"a": 2}),
            ]
        )
        file_path = "s3://wq-services/datacubes/chl-2.zarr"
        self.assertEqual(
            Config(name="<computed>", settings={"a": 1, "b": 2}),
            config_list.compute_config(file_path),
        )

        # global ignores
        file_path = "s3://wq-services/datacubes/chl-2.txt"
        self.assertEqual(
            Config(name="<computed>", settings={"a": 2, "b": 1}),
            config_list.compute_config(file_path),
        )

    def test_split_global(self):
        config_list = ConfigList(
            [
                Config(settings={"a": 1, "b": 1}),
                Config(files=["**/datacubes/*.zarr"], settings={"b": 2}),
                Config(ignores=["**/chl-?.*"], settings={"a": 2}),
                Config(ignores=["**/chl-?.txt"]),  # global ignores
            ]
        )

        global_filter, regular_config_list = config_list.split_global()
        self.assertEqual(
            ConfigList(
                [
                    Config(settings={"a": 1, "b": 1}),
                    Config(files=["**/datacubes/*.zarr"], settings={"b": 2}),
                    Config(ignores=["**/chl-?.*"], settings={"a": 2}),
                ]
            ),
            regular_config_list,
        )

        self.assertEqual(GlobalFilter(set(), {"**/chl-?.txt"}), global_filter)
        self.assertEqual(
            True, global_filter.accept("s3://wq-services/datacubes/chl-2.zarr")
        )
        self.assertEqual(
            False, global_filter.accept("s3://wq-services/datacubes/chl-2.txt")
        )
