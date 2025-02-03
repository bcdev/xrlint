#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

from dataclasses import dataclass, field
from types import NoneType, UnionType
from typing import (
    TYPE_CHECKING,
    Any,
    Literal,
    Mapping,
    Optional,
    TypeAlias,
    Union,
    get_args,
    get_origin,
)
from unittest import TestCase

import pytest

from xrlint.util.constructible import (
    MappingConstructible,
    ValueConstructible,
    get_class_parameters,
)
from xrlint.util.serializable import JsonSerializable


@dataclass()
class UselessContainer(ValueConstructible):
    pass


@dataclass()
class RequiredPropsContainer(MappingConstructible):
    x: float
    y: float
    z: float


class NoTypesContainer(MappingConstructible):
    def __init__(self, u, v, w, /):  # positional only!
        self.u = u
        self.v = v
        self.w = w


@dataclass()
class SimpleTypesContainer(MappingConstructible, JsonSerializable):
    a: Any = None
    b: bool = False
    c: int = 0
    d: float = 0.0
    e: str = "abc"
    f: type = int
    g: Literal[0, 1, True, False, "on", "off"] = 0


@dataclass()
class ComplexTypesContainer(MappingConstructible, JsonSerializable):
    p: SimpleTypesContainer = field(default_factory=SimpleTypesContainer)
    q: dict[str, bool] = field(default_factory=dict)
    r: dict[str, SimpleTypesContainer] = field(default_factory=dict)
    s: list[int] = field(default_factory=list)
    t: list[SimpleTypesContainer] = field(default_factory=list)
    u: int | float | None = None


@dataclass()
class UnionTypesContainer(MappingConstructible, JsonSerializable):
    m: SimpleTypesContainer | ComplexTypesContainer | None = None


if TYPE_CHECKING:
    # make IDEs and flake8 happy
    from xrlint.plugin import Plugin
    from xrlint.rule import RuleConfig


@dataclass()
class UnresolvedTypesContainer(ComplexTypesContainer, SimpleTypesContainer):
    rules: dict[str, "RuleConfig"] = field(default_factory=dict)
    plugins: dict[str, "Plugin"] = field(default_factory=dict)

    @classmethod
    def forward_refs(cls) -> Optional[Mapping[str, type]]:
        from xrlint.plugin import Plugin
        from xrlint.rule import RuleConfig

        return {
            "RuleConfig": RuleConfig,
            "Plugin": Plugin,
        }


T1: TypeAlias = int | str | Union[bool, None] | None
T2: TypeAlias = Optional[int]
T3: TypeAlias = Optional[Any]


class TypingTest(TestCase):
    def test_assumptions(self):
        # self.assertTrue(isinstance(Any, type))
        self.assertTrue(isinstance(UnionType, type))
        self.assertTrue(not isinstance(Union, type))
        self.assertTrue(not isinstance(Union, UnionType))
        self.assertTrue(Union != UnionType)

        self.assertEqual(None, get_origin("NoTypesContainer"))
        self.assertEqual(None, get_origin("dict"))
        self.assertEqual(dict, get_origin(dict[str, "NoTypesContainer"]))
        self.assertEqual(
            (str, "NoTypesContainer"), get_args(dict[str, "NoTypesContainer"])
        )

        self.assertEqual(Union, get_origin(T1))
        self.assertEqual({bool, int, str, NoneType}, set(get_args(T1)))

        self.assertEqual(Union, get_origin(T2))
        self.assertEqual({int, NoneType}, set(get_args(T2)))

        self.assertEqual(Union, get_origin(T3))
        self.assertEqual({Any, NoneType}, set(get_args(T3)))


# noinspection PyMethodMayBeStatic
class ValueConstructibleTest(TestCase):
    def test_useless_ok(self):
        container = UselessContainer()
        self.assertIs(container, UselessContainer.from_value(container))

    # noinspection PyMethodMayBeStatic
    def test_useless_fail(self):
        with pytest.raises(
            TypeError,
            match="uc must be of type UselessContainer, but got None",
        ):
            UselessContainer.from_value(None, value_name="uc")

        with pytest.raises(
            TypeError,
            match="uc must be of type UselessContainer, but got bool",
        ):
            UselessContainer.from_value(True, value_name="uc")

        with pytest.raises(
            TypeError,
            match="uc must be of type UselessContainer, but got int",
        ):
            UselessContainer.from_value(1, value_name="uc")

        with pytest.raises(
            TypeError,
            match="uc must be of type UselessContainer, but got float",
        ):
            UselessContainer.from_value(0.1, value_name="uc")

        with pytest.raises(
            TypeError,
            match="uc must be of type UselessContainer, but got str",
        ):
            UselessContainer.from_value("abc", value_name="uc")

        with pytest.raises(
            TypeError,
            match="utc must be of type UselessContainer, but got dict",
        ):
            UselessContainer.from_value({}, value_name="utc")

        with pytest.raises(
            TypeError,
            match="uc must be of type UselessContainer, but got list",
        ):
            UselessContainer.from_value([], value_name="uc")

        with pytest.raises(
            TypeError,
            match="utc must be of type UselessContainer, but got object",
        ):
            UselessContainer.from_value(object(), value_name="utc")

        with pytest.raises(
            TypeError,
            match="utc must be of type UselessContainer, but got type",
        ):
            UselessContainer.from_value(int, value_name="utc")

        with pytest.raises(
            TypeError,
            match="utc must be of type UselessContainer, but got type",
        ):
            UselessContainer.from_value(UselessContainer, value_name="utc")

    def test_required_props_ok(self):
        rpc = RequiredPropsContainer.from_value({"x": 12.0, "y": 23.0, "z": 34.0})
        self.assertEqual(RequiredPropsContainer(x=12.0, y=23.0, z=34.0), rpc)

    # noinspection PyMethodMayBeStatic
    def test_required_props_fail(self):
        with pytest.raises(
            TypeError,
            match=(
                r"missing value for required property rpc.y"
                r" of type RequiredPropsContainer \| dict\[str, Any\]"
            ),
        ):
            RequiredPropsContainer.from_value({"x": 12.0, "z": 34.0}, "rpc")

    def test_no_types_ok(self):
        ntc = NoTypesContainer.from_value(dict(u=True, v=654, w="abc"))
        self.assertEqual(True, ntc.u)
        self.assertEqual(654, ntc.v)
        self.assertEqual("abc", ntc.w)


class MappingConstructibleTest(TestCase):
    def test_simple_ok(self):
        kwargs = dict(a="?", b=True, c=12, d=34.56, e="uvw", f=bytes, g="on")
        container = SimpleTypesContainer(**kwargs)
        self.assertEqual(container, SimpleTypesContainer.from_value(kwargs))
        self.assertIs(container, SimpleTypesContainer.from_value(container))

    def test_complex_ok(self):
        kwargs = {
            "p": {"a": None, "b": False, "c": 0, "d": 0.0, "e": "abc"},
            "q": {"p": True, "q": False},
            "r": {
                "u": {"a": None, "b": False, "c": 0, "d": 0.0, "e": "abc"},
                "v": {"a": None, "b": False, "c": 0, "d": 0.0, "e": "abc"},
            },
            "s": [1, 2, 3],
            "t": [
                {"a": None, "b": False, "c": 5, "d": 6.7, "e": "abc"},
                {"a": None, "b": False, "c": 8, "d": 9.1, "e": "abc", "f": str},
            ],
        }
        expected_container = ComplexTypesContainer(
            p=SimpleTypesContainer(a=None, b=False, c=0, d=0.0, e="abc"),
            q={"p": True, "q": False},
            r={
                "u": SimpleTypesContainer(a=None, b=False, c=0, d=0.0, e="abc"),
                "v": SimpleTypesContainer(a=None, b=False, c=0, d=0.0, e="abc"),
            },
            s=[1, 2, 3],
            t=[
                SimpleTypesContainer(a=None, b=False, c=5, d=6.7, e="abc"),
                SimpleTypesContainer(a=None, b=False, c=8, d=9.1, e="abc", f=str),
            ],
            u=None,
        )
        self.assertEqual(expected_container, ComplexTypesContainer.from_value(kwargs))
        self.assertIs(
            expected_container, ComplexTypesContainer.from_value(expected_container)
        )

    def test_union_ok(self):
        expected_union = UnionTypesContainer(m=SimpleTypesContainer())
        self.assertEqual(
            expected_union,
            UnionTypesContainer.from_value({"m": SimpleTypesContainer()}),
        )
        self.assertIs(expected_union, UnionTypesContainer.from_value(expected_union))

        expected_union = UnionTypesContainer(m=ComplexTypesContainer())
        self.assertEqual(
            expected_union,
            UnionTypesContainer.from_value({"m": ComplexTypesContainer()}),
        )
        self.assertIs(expected_union, UnionTypesContainer.from_value(expected_union))

        expected_union = UnionTypesContainer(m=None)
        self.assertEqual(
            expected_union,
            UnionTypesContainer.from_value({"m": None}),
        )
        self.assertIs(expected_union, UnionTypesContainer.from_value(expected_union))

    # noinspection PyMethodMayBeStatic
    def test_simple_fail(self):
        with pytest.raises(
            TypeError,
            match=(
                r"stc.b must be of type SimpleTypesContainer | dict\[str, Any\],"
                r" but got None"
            ),
        ):
            SimpleTypesContainer.from_value({"b": None}, value_name="stc")

        with pytest.raises(
            TypeError,
            match=r"stc.g must be one of 0, 1, True, False, 'on', 'off', but got 74",
        ):
            SimpleTypesContainer.from_value({"g": 74}, value_name="stc")

        with pytest.raises(
            TypeError, match="x is not a member of stc of type SimpleTypesContainer"
        ):
            SimpleTypesContainer.from_value({"x": 12}, value_name="stc")

        with pytest.raises(
            TypeError, match="x, y are not members of stc of type SimpleTypesContainer"
        ):
            SimpleTypesContainer.from_value({"x": 12, "y": 34}, value_name="stc")

        with pytest.raises(
            TypeError,
            match=(
                "mappings used to instantiate stc of type SimpleTypesContainer"
                " must have keys of type str, but found key of type int"
            ),
        ):
            SimpleTypesContainer.from_value({12: "x"}, value_name="stc")

        with pytest.raises(
            TypeError,
            match=(
                r"stc must be of type SimpleTypesContainer | dict\[str, Any\],"
                r" but got type"
            ),
        ):
            SimpleTypesContainer.from_value(SimpleTypesContainer, value_name="stc")

        with pytest.raises(
            TypeError,
            match="stc.f must be of type type, but got str",
        ):
            SimpleTypesContainer.from_value({"f": "pippo"}, value_name="stc")

    # noinspection PyMethodMayBeStatic
    def test_complex_fail(self):
        with pytest.raises(
            TypeError,
            match="keys of ctc.q must be of type str, but got bool",
        ):
            ComplexTypesContainer.from_value({"q": {True: False}}, value_name="ctc")

        with pytest.raises(
            TypeError,
            match=r"ctc.q\['x'\] must be of type bool, but got float",
        ):
            ComplexTypesContainer.from_value({"q": {"x": 2.3}}, value_name="ctc")

        with pytest.raises(
            TypeError,
            match=r"ctc.s\[1\] must be of type int, but got str",
        ):
            ComplexTypesContainer.from_value({"s": [1, "x", 3]}, value_name="ctc")

    # noinspection PyMethodMayBeStatic
    def test_union_fail(self):
        with pytest.raises(
            TypeError,
            match=(
                r"utc must be of type UnionTypesContainer | dict\[str, Any\],"
                r" but got int"
            ),
        ):
            UnionTypesContainer.from_value(21, value_name="utc")

        with pytest.raises(
            TypeError,
            match=(
                "utc.m must be of type SimpleTypesContainer"
                " | ComplexTypesContainer"
                " | None,"
                " but got str"
            ),
        ):
            UnionTypesContainer.from_value({"m": "pippo"}, value_name="utc")

    def test_get_class_parameters_is_cached(self):
        ctc_param = ComplexTypesContainer.class_parameters()
        stc_param = SimpleTypesContainer.class_parameters()
        self.assertIs(stc_param, SimpleTypesContainer.class_parameters())
        self.assertIs(ctc_param, ComplexTypesContainer.class_parameters())
        self.assertIsNot(ctc_param, stc_param)


class GetClassParametersTest(TestCase):
    def test_resolves_types(self):
        ctc_params = get_class_parameters(
            UnresolvedTypesContainer,
            forward_refs=UnresolvedTypesContainer.forward_refs(),
        )
        # order is important!
        self.assertEqual(
            [
                "a",
                "b",
                "c",
                "d",
                "e",
                "f",
                "g",
                "p",
                "q",
                "r",
                "s",
                "t",
                "u",
                "rules",
                "plugins",
            ],
            list(ctc_params.keys()),
        )
        for k, v in ctc_params.items():
            self.assertIsNotNone(v, msg=f"ctc_params[{k!r}]")
