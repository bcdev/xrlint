#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

from typing import Any
from unittest import TestCase

import pytest
import xarray as xr

from xrlint.config import Config, ConfigObject, get_core_config_object
from xrlint.constants import CORE_PLUGIN_NAME
from xrlint.plugin import Plugin, new_plugin
from xrlint.processor import ProcessorOp, define_processor
from xrlint.result import Message
from xrlint.rule import Rule, RuleConfig
from xrlint.util.filefilter import FileFilter


# noinspection PyMethodMayBeStatic
class ConfigObjectTest(TestCase):
    def test_class_props(self):
        self.assertEqual("config_obj", ConfigObject.value_name())
        self.assertEqual("ConfigObject | dict | None", ConfigObject.value_type_name())

    def test_defaults(self):
        config_obj = ConfigObject()
        self.assertEqual(None, config_obj.name)
        self.assertEqual(None, config_obj.files)
        self.assertEqual(None, config_obj.ignores)
        self.assertEqual(None, config_obj.linter_options)
        self.assertEqual(None, config_obj.opener_options)
        self.assertEqual(None, config_obj.processor)
        self.assertEqual(None, config_obj.plugins)
        self.assertEqual(None, config_obj.rules)

    def test_get_plugin(self):
        config_obj = get_core_config_object()
        plugin = config_obj.get_plugin(CORE_PLUGIN_NAME)
        self.assertIsInstance(plugin, Plugin)

        with pytest.raises(ValueError, match="unknown plugin 'xcube'"):
            config_obj.get_plugin("xcube")

    def test_get_rule(self):
        config_obj = get_core_config_object()
        rule = config_obj.get_rule("var-flags")
        self.assertIsInstance(rule, Rule)

        with pytest.raises(ValueError, match="unknown rule 'foo'"):
            config_obj.get_rule("foo")

    def test_get_processor_op(self):
        class MyProc(ProcessorOp):
            def preprocess(
                self, file_path: str, opener_options: dict[str, Any]
            ) -> list[tuple[xr.Dataset, str]]:
                pass

            def postprocess(
                self, messages: list[list[Message]], file_path: str
            ) -> list[Message]:
                pass

        processor = define_processor("myproc", op_class=MyProc)
        config_obj = ConfigObject(
            plugins=dict(
                myplugin=new_plugin("myplugin", processors=dict(myproc=processor))
            )
        )

        processor_op = config_obj.get_processor_op(MyProc())
        self.assertIsInstance(processor_op, MyProc)

        processor_op = config_obj.get_processor_op("myplugin/myproc")
        self.assertIsInstance(processor_op, MyProc)

        with pytest.raises(ValueError, match="unknown processor 'myplugin/myproc2'"):
            config_obj.get_processor_op("myplugin/myproc2")

    def test_from_value_ok(self):
        self.assertEqual(ConfigObject(), ConfigObject.from_value(None))
        self.assertEqual(ConfigObject(), ConfigObject.from_value({}))
        self.assertEqual(ConfigObject(), ConfigObject.from_value(ConfigObject()))
        self.assertEqual(
            ConfigObject(name="x"), ConfigObject.from_value(ConfigObject(name="x"))
        )
        self.assertEqual(
            ConfigObject(
                name="xXx",
                files=["**/*.zarr", "**/*.nc"],
                linter_options={"a": 4},
                opener_options={"b": 5},
                settings={"c": 6},
            ),
            ConfigObject.from_value(
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
            ConfigObject(
                rules={
                    "hello/no-spaces-in-titles": RuleConfig(severity=2),
                    "hello/time-without-tz": RuleConfig(severity=0),
                    "hello/no-empty-units": RuleConfig(
                        severity=1, args=(12,), kwargs={"indent": 4}
                    ),
                },
            ),
            ConfigObject.from_value(
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
        config_obj = ConfigObject(
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
            config_obj.to_json(),
        )

    def test_from_value_fails(self):
        with pytest.raises(
            TypeError,
            match=r"config_obj must be of type ConfigObject \| dict \| None, but got int",
        ):
            ConfigObject.from_value(4)

        with pytest.raises(
            TypeError,
            match=r"config_obj must be of type ConfigObject \| dict \| None, but got str",
        ):
            ConfigObject.from_value("abc")

        with pytest.raises(
            TypeError,
            match=r"config_obj must be of type ConfigObject \| dict \| None, but got tuple",
        ):
            ConfigObject.from_value(())

        with pytest.raises(
            TypeError,
            match=r" config_obj.linter_options must be of type dict.*, but got list",
        ):
            ConfigObject.from_value({"linter_options": [1, 2, 3]})

        with pytest.raises(
            TypeError,
            match=r" keys of config_obj.settings must be of type str, but got int",
        ):
            ConfigObject.from_value({"settings": {8: 9}})


class ConfigTest(TestCase):
    def test_from_config_ok(self):
        config = Config.from_config()
        self.assertIsInstance(config, Config)
        self.assertEqual([], config.objects)

        config = Config.from_config(
            {"ignores": ["**/*.levels"]},
            get_core_config_object(),
            "recommended",
            {"rules": {"no-empty-chunks": 2}},
        )
        self.assertIsInstance(config, Config)
        self.assertEqual(4, len(config.objects))

        config = Config.from_config(config)
        self.assertIsInstance(config, Config)
        self.assertEqual(4, len(config.objects))

        config = Config.from_config(config.objects)
        self.assertIsInstance(config, Config)
        self.assertEqual(4, len(config.objects))

        config = Config.from_config(*config.objects)
        self.assertIsInstance(config, Config)
        self.assertEqual(4, len(config.objects))

    def test_from_value_ok(self):
        config = Config.from_value([])
        self.assertIsInstance(config, Config)
        self.assertEqual([], config.objects)

        config_2 = Config.from_value(config)
        self.assertIs(config_2, config)

        config = Config.from_value([{}])
        self.assertIsInstance(config, Config)
        self.assertEqual([], config.objects)

        config_object = ConfigObject.from_value({})
        config = Config.from_value(config_object)
        self.assertIsInstance(config, Config)
        self.assertIs(config_object, config.objects[0])

    # noinspection PyMethodMayBeStatic
    def test_from_value_fail(self):
        with pytest.raises(
            TypeError,
            match=(
                r"config must be of type"
                r" Config \| ConfigObjectLike \| str \| Sequence\[ConfigObjectLike \| str\],"
                r" but got int"
            ),
        ):
            Config.from_value(264)

    def test_compute_config(self):
        config = Config([ConfigObject()])
        file_path = "s3://wq-services/datacubes/chl-2.zarr"
        self.assertEqual(ConfigObject(), config.compute_config_object(file_path))

        config = Config(
            [
                ConfigObject(ignores=["**/*.yaml"], settings={"a": 1, "b": 1}),
                ConfigObject(files=["**/datacubes/*.zarr"], settings={"b": 2}),
                ConfigObject(files=["**/*.txt"], settings={"a": 2}),
            ]
        )
        file_path = "s3://wq-services/datacubes/chl-2.zarr"
        self.assertEqual(
            ConfigObject(settings={"a": 1, "b": 2}),
            config.compute_config_object(file_path),
        )

        # global ignores
        file_path = "s3://wq-services/datacubes/chl-2.txt"
        self.assertEqual(
            ConfigObject(settings={"a": 2, "b": 1}),
            config.compute_config_object(file_path),
        )

        file_path = "s3://wq-services/datacubes/config.yaml"
        self.assertEqual(
            None,
            config.compute_config_object(file_path),
        )

    def test_split_global_filter(self):
        config = Config(
            [
                ConfigObject(files=["**/*.hdf"]),  # global file
                ConfigObject(ignores=["**/chl-?.txt"]),  # global ignores
                ConfigObject(ignores=["**/chl-?.*"], settings={"a": 2}),
                ConfigObject(settings={"a": 1, "b": 1}),
                ConfigObject(files=["**/datacubes/*.zarr"], settings={"b": 2}),
            ]
        )

        new_config, file_filter = config.split_global_filter()
        self.assertEqual(
            FileFilter.from_patterns(["**/*.hdf"], ["**/chl-?.txt"]),
            file_filter,
        )
        self.assertEqual(3, len(new_config.objects))

        new_config, file_filter = config.split_global_filter(
            default=FileFilter.from_patterns(["**/*.h5"], None)
        )
        self.assertEqual(
            FileFilter.from_patterns(["**/*.h5", "**/*.hdf"], ["**/chl-?.txt"]),
            file_filter,
        )
        self.assertEqual(3, len(new_config.objects))
