#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

from abc import ABC
from dataclasses import dataclass
from typing import Type
from unittest import TestCase

import pytest

from xrlint.operation import Operation, OperationMeta


class ThingOp(ABC):
    def do_something(self):
        pass


@dataclass(kw_only=True)
class ThingMeta(OperationMeta):
    pass


@dataclass(kw_only=True, frozen=True)
class Thing(Operation):
    meta: ThingMeta
    op_class: Type[ThingOp]

    @classmethod
    def meta_class(cls) -> Type:
        return ThingMeta

    @classmethod
    def op_base_class(cls) -> Type[ThingOp]:
        return ThingOp

    @classmethod
    def value_name(cls) -> str:
        return "thing"

    @classmethod
    def define(cls, op_class: Type[ThingOp] | None = None, **kwargs):
        return cls.define_operation(op_class, **kwargs)


class MyThingOp1(ThingOp):
    pass


class MyThingOp2(ThingOp):
    pass


# This is one way of exporting one of many things from a module
thing1 = Thing(meta=ThingMeta(name="my-thing-op-1"), op_class=MyThingOp1)
thing2 = Thing(meta=ThingMeta(name="my-thing-op-2"), op_class=MyThingOp2)


# This is the default way of exporting a single thing from a dedicated module
def export_thing() -> Thing:
    class MyThingOp3(ThingOp):
        pass

    return Thing(meta=ThingMeta(name="my-thing-op-3"), op_class=MyThingOp3)


class OperationTest(TestCase):
    def test_class_props(self):
        self.assertEqual(OperationMeta, Operation.meta_class())
        self.assertEqual(type, Operation.op_base_class())
        self.assertEqual("export_operation", Operation.op_import_attr_name())
        self.assertEqual("operation", Operation.value_name())
        self.assertEqual(
            "Operation | Type[type] | dict | str", Operation.value_type_name()
        )

    def test_from_value_ok_rule(self):
        thing1_ = Thing.from_value(thing1)
        self.assertIs(thing1_, thing1)

    def test_from_value_ok_rule_op(self):
        class MyThingOp3(ThingOp):
            pass

        meta = ThingMeta(name="my-thing-op-3")

        # This "defines" MyThingOp2 so we can create
        # instances from its operation class.
        MyThingOp3.meta = meta

        thing3 = Thing.from_value(MyThingOp3)
        self.assertIsInstance(thing3, Thing)
        self.assertIs(meta, thing3.meta)
        self.assertIs(MyThingOp3, thing3.op_class)

    def test_from_value_ok_str(self):
        thing1_ = Thing.from_value("tests.test_operation:thing1")
        self.assertIs(thing1, thing1_)
        self.assertEqual("tests.test_operation:thing1", thing1_.meta.ref)

        thing2_ = Thing.from_value("tests.test_operation:thing2")
        self.assertIs(thing2, thing2_)
        self.assertEqual("tests.test_operation:thing2", thing2_.meta.ref)

        # default attribute is "export_thing"
        thing3 = Thing.from_value("tests.test_operation")
        self.assertIsInstance(thing3, Thing)
        self.assertIs("my-thing-op-3", thing3.meta.name)
        self.assertIsInstance(thing3.op_class, type)
        self.assertEqual("tests.test_operation:export_thing", thing3.meta.ref)

    # noinspection PyMethodMayBeStatic
    def test_from_value_fails(self):
        with pytest.raises(
            TypeError, match="value must be of type Thing | str, but got int"
        ):
            Thing.from_value(73)

        class MyThing3(ThingOp):
            """This is my 3rd thing."""

        with pytest.raises(
            ValueError,
            match=r"missing thing metadata, apply define_thing\(\) to class MyThing3",
        ):
            Thing.from_value(MyThing3)

        with pytest.raises(
            TypeError,
            match=(
                r"thing must be of type Thing \| Type\[ThingOp\] \|"
                r" dict | str, but got type"
            ),
        ):
            Thing.from_value(Thing)

    def test_to_json(self):
        class MyThingOp3(ThingOp):
            """This is my 3rd thing."""

        thing3 = Thing(
            meta=ThingMeta(name="t3", ref="mypkg.things:thing3"), op_class=MyThingOp3
        )
        self.assertEqual("mypkg.things:thing3", thing3.to_json())

        rule = Thing(
            meta=ThingMeta(name="t3", description="What a thing."), op_class=MyThingOp3
        )
        self.assertEqual(
            {
                "meta": {"description": "What a thing.", "name": "t3"},
                "op_class": "<class "
                "'tests.test_operation.OperationTest.test_to_json.<locals>.MyThingOp3'>",
            },
            rule.to_json(),
        )


class OpMixinDefineTest(TestCase):
    def test_define_op(self):
        class MyThingOp3(ThingOp):
            """This is my 3rd thing."""

        value = Thing.define_operation(MyThingOp3, meta_kwargs=dict(version="1.0"))
        self.assertIsInstance(value, Thing)
        self.assertIsInstance(value.meta, ThingMeta)
        self.assertEqual("my-thing-op-3", value.meta.name)
        self.assertEqual("1.0", value.meta.version)
        self.assertEqual("This is my 3rd thing.", value.meta.description)
        self.assertIs(MyThingOp3, value.op_class)
        self.assertTrue(hasattr(MyThingOp3, "meta"))
        # noinspection PyUnresolvedReferences
        self.assertIs(value.meta, MyThingOp3.meta)

    def test_define_op_fail(self):
        class MyThingOp3(ThingOp):
            """This is my 3rd thing."""

        with pytest.raises(
            TypeError, match="registry must be a MutableMapping, but got int"
        ):
            # noinspection PyTypeChecker
            Thing.define_operation(MyThingOp3, registry=12)

    def test_decorator(self):
        class MyThingOp3(ThingOp):
            """This is my 3rd thing."""

        closure = Thing.define()
        self.assertTrue(callable(closure))
        op_class = closure(MyThingOp3)
        self.assertIs(MyThingOp3, op_class)
        self.assertTrue(hasattr(MyThingOp3, "meta"))
        # noinspection PyUnresolvedReferences
        meta = op_class.meta
        self.assertEqual("my-thing-op-3", meta.name)
        self.assertEqual("0.0.0", meta.version)
        self.assertEqual("This is my 3rd thing.", meta.description)

    # noinspection PyMethodMayBeStatic
    def test_decorator_fail(self):
        closure = Thing.define()
        with pytest.raises(
            TypeError, match="decorated thing component must be a class, but got int"
        ):
            closure(32)

        with pytest.raises(
            TypeError,
            match=(
                "decorated thing component must be a subclass of ThingOp, but got Thing"
            ),
        ):
            closure(Thing)

    def test_function(self):
        class MyThingOp3(ThingOp):
            """This is my 3rd thing."""

        thing = Thing.define(op_class=MyThingOp3)
        self.assertIsInstance(thing, Thing)
        self.assertIs(MyThingOp3, thing.op_class)
        self.assertTrue(hasattr(MyThingOp3, "meta"))
        meta = thing.meta
        # noinspection PyUnresolvedReferences
        self.assertIs(meta, thing.op_class.meta)
        self.assertEqual("my-thing-op-3", meta.name)
        self.assertEqual("0.0.0", meta.version)
        self.assertEqual("This is my 3rd thing.", meta.description)

    # noinspection PyMethodMayBeStatic
    def test_function_fail(self):
        class MyThingOp3(ThingOp):
            """This is my 3rd thing."""

        with pytest.raises(TypeError, match="op_class must be a class, but got str"):
            # noinspection PyTypeChecker
            Thing.define(op_class="Huh!")

        with pytest.raises(
            TypeError,
            match="op_class must be a subclass of ThingOp, but got TestCase",
        ):
            # noinspection PyTypeChecker
            Thing.define(TestCase)

    def test_with_registry(self):
        class Op1(ThingOp):
            """This is my 3rd thing."""

        class Op2(ThingOp):
            """This is my 3rd thing."""

        registry = {}
        t1 = Thing.define(op_class=Op1, registry=registry)
        t2 = Thing.define(op_class=Op2, registry=registry)
        self.assertIs(t1, registry["op-1"])
        self.assertIs(t2, registry["op-2"])
