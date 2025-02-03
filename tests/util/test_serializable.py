#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

from dataclasses import dataclass, field
from typing import Any, Literal
from unittest import TestCase

import pytest

from xrlint.util.serializable import JsonSerializable


class PlainSimpleTypesContainer(JsonSerializable):
    def __init__(
        self,
        a: Any = None,
        b: bool = False,
        c: int = 0,
        d: float = 0.0,
        e: str = "abc",
        f: type = int,
        g: Literal[0, 1, True, False, "on", "off"] = 0,
    ):
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.e = e
        self.f = f
        self.g = g


class PlainComplexTypesContainer(JsonSerializable):
    def __init__(
        self,
        p: PlainSimpleTypesContainer = PlainSimpleTypesContainer(),
        q: dict[str, bool] = None,
        r: dict[str, PlainSimpleTypesContainer] = None,
        s: list[int] = None,
        t: list[PlainSimpleTypesContainer] = None,
        u: int | float | None = None,
    ):
        self.p = p
        self.q = q or {}
        self.r = r or {}
        self.s = s or []
        self.t = t or []
        self.u = u


@dataclass()
class DataclassSimpleTypesContainer(JsonSerializable):
    a: Any = None
    b: bool = False
    c: int = 0
    d: float = 0.0
    e: str = "abc"
    f: type = int
    g: Literal[0, 1, True, False, "on", "off"] = 0


@dataclass()
class DataclassComplexTypesContainer(JsonSerializable):
    p: DataclassSimpleTypesContainer = field(
        default_factory=DataclassSimpleTypesContainer
    )
    q: dict[str, bool] = field(default_factory=dict)
    r: dict[str, DataclassSimpleTypesContainer] = field(default_factory=dict)
    s: list[int] = field(default_factory=list)
    t: list[DataclassSimpleTypesContainer] = field(default_factory=list)
    u: int | float | None = None


# noinspection PyMethodMayBeStatic
class JsonSerializableTest(TestCase):
    def test_plain_simple_ok(self):
        self.assertEqual(
            {
                "a": None,
                "b": False,
                "c": 0,
                "d": 0.0,
                "e": "abc",
                "f": "<class 'int'>",
                "g": 0,
            },
            PlainSimpleTypesContainer().to_json(),
        )
        self.assertEqual(
            {
                "a": "?",
                "b": True,
                "c": 12,
                "d": 34.56,
                "e": "uvw",
                "f": "<class 'bool'>",
                "g": "off",
            },
            PlainSimpleTypesContainer(
                a="?", b=True, c=12, d=34.56, e="uvw", f=bool, g="off"
            ).to_json(),
        )

    def test_plain_complex_ok(self):
        container = PlainComplexTypesContainer(
            q=dict(p=True, q=False),
            r=dict(u=PlainSimpleTypesContainer(), v=PlainSimpleTypesContainer()),
            s=[1, 2, 3],
            t=[
                PlainSimpleTypesContainer(c=5, d=6.7),
                PlainSimpleTypesContainer(c=8, d=9.1, f=PlainSimpleTypesContainer),
            ],
        )
        self.assertEqual(
            {
                "p": {
                    "a": None,
                    "b": False,
                    "c": 0,
                    "d": 0.0,
                    "e": "abc",
                    "f": "<class 'int'>",
                    "g": 0,
                },
                "q": {"p": True, "q": False},
                "r": {
                    "u": {
                        "a": None,
                        "b": False,
                        "c": 0,
                        "d": 0.0,
                        "e": "abc",
                        "f": "<class 'int'>",
                        "g": 0,
                    },
                    "v": {
                        "a": None,
                        "b": False,
                        "c": 0,
                        "d": 0.0,
                        "e": "abc",
                        "f": "<class 'int'>",
                        "g": 0,
                    },
                },
                "s": [1, 2, 3],
                "t": [
                    {
                        "a": None,
                        "b": False,
                        "c": 5,
                        "d": 6.7,
                        "e": "abc",
                        "f": "<class 'int'>",
                        "g": 0,
                    },
                    {
                        "a": None,
                        "b": False,
                        "c": 8,
                        "d": 9.1,
                        "e": "abc",
                        "f": "<class 'tests.util.test_serializable.PlainSimpleTypesContainer'>",
                        "g": 0,
                    },
                ],
                "u": None,
            },
            container.to_json(),
        )

    def test_dataclass_simple_ok(self):
        self.assertEqual(
            {},
            DataclassSimpleTypesContainer().to_json(),
        )
        self.assertEqual(
            {
                "a": "?",
                "b": True,
                "c": 12,
                "d": 34.56,
                "e": "uvw",
                "f": "<class 'bool'>",
                "g": "off",
            },
            DataclassSimpleTypesContainer(
                a="?", b=True, c=12, d=34.56, e="uvw", f=bool, g="off"
            ).to_json(),
        )

    def test_dataclass_complex_ok(self):
        container = DataclassComplexTypesContainer(
            q=dict(p=True, q=False),
            r=dict(
                u=DataclassSimpleTypesContainer(), v=DataclassSimpleTypesContainer()
            ),
            s=[1, 2, 3],
            t=[
                DataclassSimpleTypesContainer(c=5, d=6.7),
                DataclassSimpleTypesContainer(
                    c=8, d=9.1, f=DataclassSimpleTypesContainer
                ),
            ],
        )
        self.assertEqual(
            {
                "p": {},
                "q": {"p": True, "q": False},
                "r": {"u": {}, "v": {}},
                "s": [1, 2, 3],
                "t": [
                    {"c": 5, "d": 6.7},
                    {
                        "c": 8,
                        "d": 9.1,
                        "f": (
                            "<class 'tests.util.test_serializable"
                            ".DataclassSimpleTypesContainer'>"
                        ),
                    },
                ],
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
            Problematic(data=object()).to_json(value_name="problematic")
