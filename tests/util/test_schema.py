from unittest import TestCase

import pytest

from xrlint.util.schema import schema


class SchemaTest(TestCase):
    def test_type_name(self):
        self.assertEqual({}, schema())
        self.assertEqual({}, schema(type=None))
        self.assertEqual({"type": "null"}, schema("null"))
        self.assertEqual({"type": "boolean"}, schema("boolean"))
        self.assertEqual({"type": "integer"}, schema("integer"))
        self.assertEqual({"type": "number"}, schema("number"))
        self.assertEqual({"type": "string"}, schema("string"))
        self.assertEqual({"type": "object"}, schema("object"))
        self.assertEqual({"type": "array"}, schema("array"))

    def test_type_name_list(self):
        self.assertEqual({}, schema())
        self.assertEqual({}, schema([]))
        self.assertEqual({"type": ["array", "string"]}, schema(["array", "string"]))

    # noinspection PyTypeChecker,PyMethodMayBeStatic
    def test_type_name_invalid(self):
        with pytest.raises(
            TypeError, match="type must be of type str|list[str], but was str"
        ):
            schema(type=str)
        with pytest.raises(
            ValueError,
            match=(
                "type name must be one of "
                "'null', 'boolean', 'integer', 'number',"
                " 'string', 'array', 'object',"
                " but was 'float'"
            ),
        ):
            schema(type="float")

    # noinspection PyTypeChecker,PyMethodMayBeStatic
    def test_type_name_list_invalid(self):
        with pytest.raises(
            TypeError, match="type must be of type str|list[str], but was int"
        ):
            schema(type=["string", 2])
        with pytest.raises(
            ValueError,
            match=(
                "type name must be one of"
                " 'null', 'boolean', 'integer', 'number',"
                " 'string', 'array', 'object',"
                " but was 'list'"
            ),
        ):
            schema(type=["string", "list"])

    def test_properties(self):
        self.assertEqual({}, schema(properties=None))
        self.assertEqual({"properties": {}}, schema(properties={}))
        self.assertEqual(
            {"properties": {"a": {"type": "string"}, "b": {}}},
            schema(properties={"a": schema("string"), "b": schema()}),
        )
