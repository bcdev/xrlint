from typing import Any
from unittest import TestCase

import pytest
import xarray as xr

from xrlint.plugin import Plugin
from xrlint.plugin import PluginMeta
from xrlint.processor import Processor
from xrlint.processor import ProcessorMeta
from xrlint.processor import ProcessorOp
from xrlint.processor import define_processor
from xrlint.result import Message


class ProcessorTest(TestCase):

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
                r"component decorated by define_processor\(\)"
                r" must be a subclass of ProcessorOp"
            ),
        ):

            @define_processor()
            class MyProcessorOp:
                pass

    def test_define_processor_with_plugin(self):
        plugin = Plugin(meta=PluginMeta(name="my-plugin"))

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
