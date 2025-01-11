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
    a: Optional[Any] = None
    b: bool = False
    c: int = 0
    d: float = 0.0
    e: str = "abc"


@dataclass()
class ComplexTypesContainer(ValueConstructible, JsonSerializable):
    f: SimpleTypesContainer = field(default_factory=SimpleTypesContainer)
    g: dict[str, bool] = field(default_factory=dict)
    h: dict[str, SimpleTypesContainer] = field(default_factory=dict)
    i: list[int] = field(default_factory=list)
    j: list[SimpleTypesContainer] = field(default_factory=list)
    k: int | float | None = None


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
            {"a": None, "b": False, "c": 0, "d": 0.0, "e": "abc"},
            SimpleTypesContainer().to_json(),
        )
        self.assertEqual(
            {"a": "?", "b": True, "c": 12, "d": 34.56, "e": "uvw"},
            SimpleTypesContainer(a="?", b=True, c=12, d=34.56, e="uvw").to_json(),
        )

    def test_complex_ok(self):
        container = ComplexTypesContainer(
            g=dict(p=True, q=False),
            h=dict(u=SimpleTypesContainer(), v=SimpleTypesContainer()),
            i=[1, 2, 3],
            j=[SimpleTypesContainer(c=5, d=6.7), SimpleTypesContainer(c=8, d=9.1)],
        )
        self.assertEqual(
            {
                "f": {"a": None, "b": False, "c": 0, "d": 0.0, "e": "abc"},
                "g": {"p": True, "q": False},
                "h": {
                    "u": {"a": None, "b": False, "c": 0, "d": 0.0, "e": "abc"},
                    "v": {"a": None, "b": False, "c": 0, "d": 0.0, "e": "abc"},
                },
                "i": [1, 2, 3],
                "j": [
                    {"a": None, "b": False, "c": 5, "d": 6.7, "e": "abc"},
                    {"a": None, "b": False, "c": 8, "d": 9.1, "e": "abc"},
                ],
                "k": None,
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
                " None|bool|int|float|str|dict|list|tuple, but was object"
            ),
        ):
            Problematic(data=object()).to_json(name="problematic")


class ValueConstructibleTest(TestCase):

    def test_simple_ok(self):
        kwargs = dict(a="?", b=True, c=12, d=34.56, e="uvw")
        container = SimpleTypesContainer(**kwargs)
        self.assertEqual(container, SimpleTypesContainer.from_value(kwargs))
        self.assertIs(container, SimpleTypesContainer.from_value(container))

    def test_complex_ok(self):
        kwargs = {
            "f": {"a": None, "b": False, "c": 0, "d": 0.0, "e": "abc"},
            "g": {"p": True, "q": False},
            "h": {
                "u": {"a": None, "b": False, "c": 0, "d": 0.0, "e": "abc"},
                "v": {"a": None, "b": False, "c": 0, "d": 0.0, "e": "abc"},
            },
            "i": [1, 2, 3],
            "j": [
                {"a": None, "b": False, "c": 5, "d": 6.7, "e": "abc"},
                {"a": None, "b": False, "c": 8, "d": 9.1, "e": "abc"},
            ],
        }
        expected_container = ComplexTypesContainer(
            f=SimpleTypesContainer(a=None, b=False, c=0, d=0.0, e="abc"),
            g={"p": True, "q": False},
            h={
                "u": SimpleTypesContainer(a=None, b=False, c=0, d=0.0, e="abc"),
                "v": SimpleTypesContainer(a=None, b=False, c=0, d=0.0, e="abc"),
            },
            i=[1, 2, 3],
            j=[
                SimpleTypesContainer(a=None, b=False, c=5, d=6.7, e="abc"),
                SimpleTypesContainer(a=None, b=False, c=8, d=9.1, e="abc"),
            ],
            k=None,
        )
        self.assertEqual(expected_container, ComplexTypesContainer.from_value(kwargs))
        self.assertIs(
            expected_container, ComplexTypesContainer.from_value(expected_container)
        )

    # noinspection PyMethodMayBeStatic
    def test_fail(self):
        with pytest.raises(
            TypeError, match="stc must be of type SimpleTypesContainer, but was None"
        ):
            SimpleTypesContainer.from_value(None, name="stc")

        with pytest.raises(
            TypeError, match="stc must be of type SimpleTypesContainer, but was bool"
        ):
            SimpleTypesContainer.from_value(True, name="stc")

        with pytest.raises(
            TypeError, match="stc must be of type SimpleTypesContainer, but was int"
        ):
            SimpleTypesContainer.from_value(1, name="stc")

        with pytest.raises(
            TypeError, match="stc must be of type SimpleTypesContainer, but was float"
        ):
            SimpleTypesContainer.from_value(0.1, name="stc")

        with pytest.raises(
            TypeError, match="stc must be of type SimpleTypesContainer, but was str"
        ):
            SimpleTypesContainer.from_value("abc", name="stc")

        with pytest.raises(
            TypeError, match="stc must be of type SimpleTypesContainer, but was list"
        ):
            SimpleTypesContainer.from_value([], name="stc")

        with pytest.raises(
            TypeError, match="stc.b must be of type SimpleTypesContainer, but was None"
        ):
            SimpleTypesContainer.from_value({"b": None}, name="stc")

        with pytest.raises(
            TypeError, match="x is not a member of stc of type SimpleTypesContainer"
        ):
            SimpleTypesContainer.from_value({"x": 12}, name="stc")

        with pytest.raises(
            TypeError, match="x, y are not members of stc of type SimpleTypesContainer"
        ):
            SimpleTypesContainer.from_value({"x": 12, "y": 34}, name="stc")

        with pytest.raises(
            TypeError,
            match="stc of type dict must have keys of type str, but key type was int",
        ):
            SimpleTypesContainer.from_value({12: "x"}, name="stc")

        with pytest.raises(
            TypeError,
            match="stc must be of type SimpleTypesContainer, but was type",
        ):
            SimpleTypesContainer.from_value(SimpleTypesContainer, name="stc")

        with pytest.raises(
            TypeError,
            match=(
                "stc must be of type SimpleTypesContainer,"
                " but was ComplexTypesContainer"
            ),
        ):
            SimpleTypesContainer.from_value(ComplexTypesContainer(), name="stc")

    def test_get_properties(self):
        @dataclass()
        class CombinedTypesContainer(SimpleTypesContainer, ComplexTypesContainer):
            pass

        properties = CombinedTypesContainer._get_properties()
        self.assertEqual(
            {
                "a": Optional[Any],
                "b": bool,
                "c": int,
                "d": float,
                "e": str,
                "f": SimpleTypesContainer,
                "g": dict[str, bool],
                "h": dict[str, SimpleTypesContainer],
                "i": list[int],
                "j": list[SimpleTypesContainer],
                "k": int | float | None,
            },
            properties,
        )

        other_properties = SimpleTypesContainer._get_properties()
        self.assertIs(other_properties, SimpleTypesContainer._get_properties())

        self.assertIs(properties, CombinedTypesContainer._get_properties())
