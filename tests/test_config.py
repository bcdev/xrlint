from unittest import TestCase

import pytest

from xrlint.config import Config, ConfigList
from xrlint.rule import RuleConfig
from xrlint.util.filefilter import FileFilter


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
        self.assertEqual(
            Config(
                rules={
                    "hello/no-spaces-in-titles": RuleConfig(severity=2),
                    "hello/time-without-tz": RuleConfig(severity=0),
                    "hello/no-empty-units": RuleConfig(
                        severity=1, args=(12,), kwargs={"indent": 4}
                    ),
                },
            ),
            Config.from_value(
                {
                    "rules": {
                        "hello/no-spaces-in-titles": 2,
                        "hello/time-without-tz": "off",
                        "hello/no-empty-units": ["warn", 12, {"indent": 4}],
                    },
                }
            ),
        )

    def test_to_json(self):
        config = Config(
            name="xXx",
            files=["**/*.zarr", "**/*.nc"],
            linter_options={"a": 4},
            opener_options={"b": 5},
            settings={"c": 6},
            rules={
                "hello/no-spaces-in-titles": RuleConfig(severity=2),
                "hello/time-without-tz": RuleConfig(severity=0),
                "hello/no-empty-units": RuleConfig(
                    severity=1, args=(12,), kwargs={"indent": 4}
                ),
            },
        )
        self.assertEqual(
            {
                "name": "xXx",
                "files": ["**/*.zarr", "**/*.nc"],
                "linter_options": {"a": 4},
                "opener_options": {"b": 5},
                "settings": {"c": 6},
                "rules": {
                    "hello/no-empty-units": [1, 12, {"indent": 4}],
                    "hello/no-spaces-in-titles": 2,
                    "hello/time-without-tz": 0,
                },
            },
            config.to_json(),
        )

    def test_from_value_fails(self):
        with pytest.raises(
            TypeError,
            match=r"config must be of type Config \| dict \| None, but got int",
        ):
            Config.from_value(4)

        with pytest.raises(
            TypeError,
            match=r"config must be of type Config \| dict \| None, but got str",
        ):
            Config.from_value("abc")

        with pytest.raises(
            TypeError,
            match=r"config must be of type Config \| dict \| None, but got tuple",
        ):
            Config.from_value(())

        with pytest.raises(
            TypeError,
            match=r" config.linter_options must be of type dict.*, but got list",
        ):
            Config.from_value({"linter_options": [1, 2, 3]})

        with pytest.raises(
            TypeError,
            match=r" keys of config.settings must be of type str, but got int",
        ):
            Config.from_value({"settings": {8: 9}})


class ConfigListTest(TestCase):
    def test_from_value_ok(self):
        config_list = ConfigList.from_value([])
        self.assertIsInstance(config_list, ConfigList)
        self.assertEqual([], config_list.configs)

        config_list_2 = ConfigList.from_value(config_list)
        self.assertIs(config_list_2, config_list)

        config_list = ConfigList.from_value([{}])
        self.assertIsInstance(config_list, ConfigList)
        self.assertEqual([Config()], config_list.configs)

    # noinspection PyMethodMayBeStatic
    def test_from_value_fail(self):
        with pytest.raises(
            TypeError,
            match=(
                r"config_list must be of type"
                r" ConfigList \| list\[Config \| dict\], but got dict"
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

    def test_get_global_filter(self):
        config_list = ConfigList(
            [
                Config(files=["**/*.hdf"]),  # global file
                Config(ignores=["**/chl-?.txt"]),  # global ignores
                Config(ignores=["**/chl-?.*"], settings={"a": 2}),
                Config(settings={"a": 1, "b": 1}),
                Config(files=["**/datacubes/*.zarr"], settings={"b": 2}),
            ]
        )

        file_filter = config_list.get_global_filter()
        self.assertEqual(
            FileFilter.from_patterns(["**/*.hdf"], ["**/chl-?.txt"]),
            file_filter,
        )

        file_filter = config_list.get_global_filter(
            default=FileFilter.from_patterns(["**/*.h5"], None)
        )
        self.assertEqual(
            FileFilter.from_patterns(["**/*.h5", "**/*.hdf"], ["**/chl-?.txt"]),
            file_filter,
        )
