#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

from typing import Any
from unittest import TestCase

import pytest
import xarray as xr

from xrlint.plugin import new_plugin
from xrlint.processor import Processor, ProcessorMeta, ProcessorOp, define_processor
from xrlint.result import Message


class ProcessorMetaTest(TestCase):
    def test_class_props(self):
        self.assertEqual("processor_meta", ProcessorMeta.value_name())
        self.assertEqual("ProcessorMeta | dict", ProcessorMeta.value_type_name())


class ProcessorTest(TestCase):
    def test_class_props(self):
        self.assertEqual("processor", Processor.value_name())
        self.assertEqual(
            "Processor | Type[ProcessorOp] | dict | str", Processor.value_type_name()
        )

    def test_define_processor(self):
        registry = {}

        class MyProcessorOp(ProcessorOp):
            def preprocess(
                self, file_path: str, opener_options: dict[str, Any]
            ) -> list[tuple[xr.Dataset, str]]:
                return []

            def postprocess(
                self, messages: list[list[Message]], file_path: str
            ) -> list[Message]:
                return []

        processor = define_processor(op_class=MyProcessorOp, registry=registry)

        self.assertTrue(hasattr(MyProcessorOp, "meta"))
        # noinspection PyUnresolvedReferences
        meta = MyProcessorOp.meta
        self.assertIsInstance(meta, ProcessorMeta)
        self.assertEqual("my-processor-op", meta.name)
        processor2: Processor = registry.get("my-processor-op")
        self.assertIs(processor, processor2)

    def test_define_processor_as_decorator(self):
        registry = {}

        @define_processor(registry=registry)
        class MyProcessorOp(ProcessorOp):
            def preprocess(
                self, file_path: str, opener_options: dict[str, Any]
            ) -> list[tuple[xr.Dataset, str]]:
                return []

            def postprocess(
                self, messages: list[list[Message]], file_path: str
            ) -> list[Message]:
                return []

        self.assertTrue(hasattr(MyProcessorOp, "meta"))
        # noinspection PyUnresolvedReferences
        meta = MyProcessorOp.meta
        self.assertIsInstance(meta, ProcessorMeta)
        self.assertEqual("my-processor-op", meta.name)
        processor: Processor = registry.get("my-processor-op")
        self.assertIsInstance(processor, Processor)
        self.assertIs(MyProcessorOp, processor.op_class)

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def test_define_processor_as_decorator_fail(self):
        with pytest.raises(
            TypeError,
            match=(
                "decorated processor component must be a subclass of ProcessorOp,"
                " but got MyProcessorOp"
            ),
        ):

            @define_processor()
            class MyProcessorOp:
                pass

    def test_define_processor_with_plugin(self):
        plugin = new_plugin(name="my-plugin")

        @plugin.define_processor()
        class MyProcessorOp(ProcessorOp):
            def preprocess(
                self, file_path: str, opener_options: dict[str, Any]
            ) -> list[tuple[xr.Dataset, str]]:
                return []

            def postprocess(
                self, messages: list[list[Message]], file_path: str
            ) -> list[Message]:
                return []

        self.assertTrue(hasattr(MyProcessorOp, "meta"))
        # noinspection PyUnresolvedReferences
        meta = MyProcessorOp.meta
        self.assertIsInstance(meta, ProcessorMeta)
        self.assertEqual("my-processor-op", meta.name)
        processor: Processor = plugin.processors.get("my-processor-op")
        self.assertIsInstance(processor, Processor)
        self.assertIs(MyProcessorOp, processor.op_class)
