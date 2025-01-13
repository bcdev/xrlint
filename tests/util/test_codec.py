from dataclasses import dataclass, field
from types import NoneType, UnionType
from typing import (
    Any,
    Union,
    Optional,
    TypeAlias,
    get_args,
    get_origin,
    Mapping,
    TYPE_CHECKING,
)
from unittest import TestCase

import pytest

from xrlint.util.codec import (
    ValueConstructible,
    JsonSerializable,
    MappingConstructible,
    get_class_parameters,
)


@dataclass()
class UselessContainer(ValueConstructible):
    pass


@dataclass()
class SimpleTypesContainer(MappingConstructible, JsonSerializable):
    a: Any = None
    b: bool = False
    c: int = 0
    d: float = 0.0
    e: str = "abc"
    f: type = int


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


@dataclass()
class RequiredPropsContainer(MappingConstructible, JsonSerializable):
    x: float
    y: float
    z: float


@dataclass()
class NoTypesContainer(MappingConstructible, JsonSerializable):
    u = 0
    v = 0
    w = 0


if TYPE_CHECKING:
    # make IDEs and flake8 happy
    from xrlint.rule import RuleConfig
    from xrlint.plugin import Plugin


@dataclass()
class UnresolvedTypesContainer(ComplexTypesContainer, SimpleTypesContainer):
    rules: dict[str, "RuleConfig"] = field(default_factory=dict)
    plugins: dict[str, "Plugin"] = field(default_factory=dict)

    @classmethod
    def _get_forward_refs(cls) -> Optional[Mapping[str, type]]:
        from xrlint.rule import RuleConfig
        from xrlint.plugin import Plugin

        return {
            "RuleConfig": RuleConfig,
            "Plugin": Plugin,
        }


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


class MappingConstructibleTest(TestCase):

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
        ctc_param = ComplexTypesContainer._get_class_parameters()
        stc_param = SimpleTypesContainer._get_class_parameters()
        self.assertIs(stc_param, SimpleTypesContainer._get_class_parameters())
        self.assertIs(ctc_param, ComplexTypesContainer._get_class_parameters())
        self.assertIsNot(ctc_param, stc_param)


class GetClassParametersTest(TestCase):

    def test_resolves_types(self):
        ctc_params = get_class_parameters(
            UnresolvedTypesContainer,
            forward_refs=UnresolvedTypesContainer._get_forward_refs(),
        )
        expected_annotations = {
            "a": "typing.Any",
            "b": "<class 'bool'>",
            "c": "<class 'int'>",
            "d": "<class 'float'>",
            "e": "<class 'str'>",
            "f": "<class 'type'>",
            "p": "<class 'tests.util.test_codec.SimpleTypesContainer'>",
            "q": "dict[str, bool]",
            "r": "dict[str, tests.util.test_codec.SimpleTypesContainer]",
            "s": "list[int]",
            "t": "list[tests.util.test_codec.SimpleTypesContainer]",
            "u": "int | float | None",
            "rules": "dict[str, xrlint.rule.RuleConfig]",
            "plugins": "dict[str, xrlint.plugin.Plugin]",
        }
        self.assertEqual(
            expected_annotations,
            {k: str(v.annotation) for k, v in ctc_params.items()},
        )
