from dataclasses import dataclass, field
from types import NoneType, UnionType
from typing import Any, Union, Optional, TypeAlias, get_args, get_origin
from unittest import TestCase

import pytest

from xrlint.util.codec import (
    ValueConstructible,
    JsonSerializable,
)


@dataclass()
class SimpleTypesContainer(ValueConstructible, JsonSerializable):
    a: Any = None
    b: bool = False
    c: int = 0
    d: float = 0.0
    e: str = "abc"
    f: type = int


@dataclass()
class ComplexTypesContainer(ValueConstructible, JsonSerializable):
    p: SimpleTypesContainer = field(default_factory=SimpleTypesContainer)
    q: dict[str, bool] = field(default_factory=dict)
    r: dict[str, SimpleTypesContainer] = field(default_factory=dict)
    s: list[int] = field(default_factory=list)
    t: list[SimpleTypesContainer] = field(default_factory=list)
    u: int | float | None = None


T1: TypeAlias = int | str | Union[bool, None] | None
T2: TypeAlias = Optional[int]
T3: TypeAlias = Optional[Any]


class TypingTest(TestCase):
    def test_assumptions(self):
        self.assertTrue(isinstance(Any, type))
        self.assertTrue(isinstance(UnionType, type))
        self.assertTrue(not isinstance(Union, type))
        self.assertTrue(not isinstance(Union, UnionType))
        self.assertTrue(Union != UnionType)

        self.assertEqual(Union, get_origin(T1))
        self.assertEqual({bool, int, str, NoneType}, set(get_args(T1)))

        self.assertEqual(Union, get_origin(T2))
        self.assertEqual({int, NoneType}, set(get_args(T2)))

        self.assertEqual(Union, get_origin(T3))
        self.assertEqual({Any, NoneType}, set(get_args(T3)))


# noinspection PyMethodMayBeStatic
class JsonSerializableTest(TestCase):
    def test_simple_ok(self):
        self.assertEqual(
            {"a": None, "b": False, "c": 0, "d": 0.0, "e": "abc", "f": "int"},
            SimpleTypesContainer().to_json(),
        )
        self.assertEqual(
            {"a": "?", "b": True, "c": 12, "d": 34.56, "e": "uvw", "f": "bool"},
            SimpleTypesContainer(
                a="?", b=True, c=12, d=34.56, e="uvw", f=bool
            ).to_json(),
        )

    def test_complex_ok(self):
        container = ComplexTypesContainer(
            q=dict(p=True, q=False),
            r=dict(u=SimpleTypesContainer(), v=SimpleTypesContainer()),
            s=[1, 2, 3],
            t=[
                SimpleTypesContainer(c=5, d=6.7),
                SimpleTypesContainer(c=8, d=9.1, f=SimpleTypesContainer),
            ],
        )
        self.assertEqual(
            {
                "p": {"a": None, "b": False, "c": 0, "d": 0.0, "e": "abc", "f": "int"},
                "q": {"p": True, "q": False},
                "r": {
                    "u": {
                        "a": None,
                        "b": False,
                        "c": 0,
                        "d": 0.0,
                        "e": "abc",
                        "f": "int",
                    },
                    "v": {
                        "a": None,
                        "b": False,
                        "c": 0,
                        "d": 0.0,
                        "e": "abc",
                        "f": "int",
                    },
                },
                "s": [1, 2, 3],
                "t": [
                    {"a": None, "b": False, "c": 5, "d": 6.7, "e": "abc", "f": "int"},
                    {
                        "a": None,
                        "b": False,
                        "c": 8,
                        "d": 9.1,
                        "e": "abc",
                        "f": "SimpleTypesContainer",
                    },
                ],
                "u": None,
            },
            container.to_json(),
        )

    def test_fail(self):
        @dataclass()
        class Problematic(JsonSerializable):
            data: Any

        with pytest.raises(
            TypeError,
            match=(
                "problematic.data must be of type"
                " None|bool|int|float|str|dict|list|tuple, but got object"
            ),
        ):
            Problematic(data=object()).to_json(name="problematic")


class ValueConstructibleTest(TestCase):

    def test_simple_ok(self):
        kwargs = dict(a="?", b=True, c=12, d=34.56, e="uvw", f=bytes)
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

    # noinspection PyMethodMayBeStatic
    def test_simple_fail(self):
        with pytest.raises(
            TypeError, match="stc must be of type SimpleTypesContainer, but got None"
        ):
            SimpleTypesContainer.from_value(None, value_name="stc")

        with pytest.raises(
            TypeError, match="stc must be of type SimpleTypesContainer, but got bool"
        ):
            SimpleTypesContainer.from_value(True, value_name="stc")

        with pytest.raises(
            TypeError, match="stc must be of type SimpleTypesContainer, but got int"
        ):
            SimpleTypesContainer.from_value(1, value_name="stc")

        with pytest.raises(
            TypeError, match="stc must be of type SimpleTypesContainer, but got float"
        ):
            SimpleTypesContainer.from_value(0.1, value_name="stc")

        with pytest.raises(
            TypeError, match="stc must be of type SimpleTypesContainer, but got str"
        ):
            SimpleTypesContainer.from_value("abc", value_name="stc")

        with pytest.raises(
            TypeError, match="stc must be of type SimpleTypesContainer, but got list"
        ):
            SimpleTypesContainer.from_value([], value_name="stc")

        with pytest.raises(
            TypeError,
            match="stc.b must be of type SimpleTypesContainer, but got None",
        ):
            SimpleTypesContainer.from_value({"b": None}, value_name="stc")

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
            match="stc must be of type SimpleTypesContainer, but got type",
        ):
            SimpleTypesContainer.from_value(SimpleTypesContainer, value_name="stc")

        with pytest.raises(
            TypeError,
            match=(
                "stc must be of type SimpleTypesContainer,"
                " but got ComplexTypesContainer"
            ),
        ):
            SimpleTypesContainer.from_value(ComplexTypesContainer(), value_name="stc")

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

    def test_signatures(self):
        @dataclass()
        class CombinedTypesContainer(ComplexTypesContainer, SimpleTypesContainer):
            pass

        sig = CombinedTypesContainer._get_signature()
        expected_sig_str = (
            "("
            "a: Any = None, "
            "b: bool = False, "
            "c: int = 0, "
            "d: float = 0.0, "
            "e: str = 'abc', "
            "f: type = <class 'int'>, "
            "p: tests.util.test_codec.SimpleTypesContainer = <factory>, "
            "q: dict[str, bool] = <factory>, "
            "r: dict[str, tests.util.test_codec.SimpleTypesContainer] = <factory>, "
            "s: list[int] = <factory>, "
            "t: list[tests.util.test_codec.SimpleTypesContainer] = <factory>, "
            "u: int | float | None = None"
            ") -> None"
        )
        self.assertEqual(
            expected_sig_str,
            str(sig),
        )

        other_sig = SimpleTypesContainer._get_signature()
        self.assertIs(other_sig, SimpleTypesContainer._get_signature())

        self.assertIs(sig, CombinedTypesContainer._get_signature())
