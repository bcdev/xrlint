#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

import unittest
from dataclasses import dataclass
from typing import Any, Callable, Final, Literal, Type

import xarray as xr

from xrlint.config import ConfigLike
from xrlint.constants import SEVERITY_ERROR
from xrlint.linter import Linter
from xrlint.plugin import new_plugin
from xrlint.result import Message
from xrlint.rule import Rule, RuleMeta, RuleOp
from xrlint.util.formatting import format_count, format_item, format_problems
from xrlint.util.naming import to_snake_case

_PLUGIN_NAME: Final = "testing"


@dataclass(frozen=True, kw_only=True)
class RuleTest:
    """A rule test case."""

    dataset: xr.Dataset
    """The dataset to verify."""

    name: str | None = None
    """A name that helps identifying the test case."""

    args: tuple | list | None = None
    """Optional positional arguments passed to the rule operation's constructor."""

    kwargs: dict[str, Any] | None = None
    """Optional keyword arguments passed to the rule operation's constructor."""

    expected: list[Message | str] | int | None = None
    """Expected messages.
    Either a list of expected message objects or
    the number of expected messages.
    Must not be provided for valid checks
    and must be provided for invalid checks.
    """


class RuleTester:
    """Utility that helps testing rules.

    Args:
        config: Optional configuration-like value.
            For more information see the
            [ConfigLike][xrlint.config.ConfigLike] type alias.
        **config_props: Individual configuration object properties.
            For more information refer to the properties of a
            [ConfigObject][xrlint.config.ConfigObject].
    """

    def __init__(self, *, config: ConfigLike = None, **config_props: Any):
        self._config = config
        self._config_props = config_props

    def run(
        self,
        rule_name: str,
        rule_op_class: Type[RuleOp],
        *,
        valid: list[RuleTest] | None = None,
        invalid: list[RuleTest] | None = None,
    ):
        """Run the given tests in `valid` and `invalid`
        against the given rule.

        Args:
            rule_name: the rule's name
            rule_op_class: a class derived from `RuleOp`
            valid: list of tests that expect no reported problems
            invalid: list of tests that expect reported problems

        Raises:
            AssertionError: if one of the checks fails
        """
        tests = self._create_tests(
            rule_name, rule_op_class, valid=valid, invalid=invalid
        )
        for test in tests.values():
            print(f"Rule {rule_name!r}: running {test.__name__}()...")
            # noinspection PyTypeChecker
            test(None)

    @classmethod
    def define_test(
        cls,
        rule_name: str,
        rule_op_class: Type[RuleOp],
        *,
        valid: list[RuleTest] | None = None,
        invalid: list[RuleTest] | None = None,
        config: ConfigLike = None,
        **config_props: Any,
    ) -> Type[unittest.TestCase]:
        """Create a `unittest.TestCase` class for the given rule and tests.

        The returned class is derived from `unittest.TestCase`
        and contains a test method for each of the tests in
        `valid` and `invalid`.

        Args:
            rule_name: the rule's name
            rule_op_class: the class derived from `RuleOp`
            valid: list of tests that expect no reported problems
            invalid: list of tests that expect reported problems
            config: Optional configuration-like value.
                For more information see the
                [ConfigLike][xrlint.config.ConfigLike] type alias.
            **config_props: Individual configuration object properties.
                For more information refer to the properties of a
                [ConfigObject][xrlint.config.ConfigObject].

        Returns:
            A new class derived from `unittest.TestCase`.
        """
        tester = RuleTester(config=config, **config_props)
        tests = tester._create_tests(
            rule_name, rule_op_class, valid=valid, invalid=invalid
        )
        # noinspection PyTypeChecker
        return type(f"{rule_op_class.__name__}Test", (unittest.TestCase,), tests)

    def _create_tests(
        self,
        rule_name: str,
        rule_op_class: Type[RuleOp],
        valid: list[RuleTest] | None,
        invalid: list[RuleTest] | None,
    ) -> dict[str, Callable[[unittest.TestCase | None], None]]:
        if hasattr(rule_op_class, "meta"):
            tests = dict([self._create_name_test(rule_name, rule_op_class)])
        else:
            tests = {}

        def make_args(checks: list[RuleTest] | None, mode: Literal["valid", "invalid"]):
            return [(check, index, mode) for index, check in enumerate(checks or [])]

        tests |= dict(
            self._create_test(rule_name, rule_op_class, *args)
            for args in make_args(valid, "valid") + make_args(invalid, "invalid")
        )
        return tests

    # noinspection PyMethodMayBeStatic
    def _create_name_test(
        self,
        rule_name: str,
        rule_op_class: Type[RuleOp],
    ) -> tuple[str, Callable]:
        test_id = "test_rule_meta"

        def test_fn(_self: unittest.TestCase):
            rule_meta: RuleMeta = getattr(rule_op_class, "meta")
            assert rule_meta.name == rule_name, (
                f"rule name expected to be {rule_name!r}, but was {rule_meta.name!r}"
            )

        test_fn.__name__ = test_id
        return test_id, test_fn

    def _create_test(
        self,
        rule_name: str,
        rule_op_class: Type[RuleOp],
        test: RuleTest,
        test_index: int,
        test_mode: Literal["valid", "invalid"],
    ) -> tuple[str, Callable]:
        test_id = _format_test_id(test, test_index, test_mode)

        def test_fn(_self: unittest.TestCase):
            error_message = self._test_rule(
                rule_name, rule_op_class, test, test_id, test_mode
            )
            if error_message:
                raise AssertionError(error_message)

        test_fn.__name__ = test_id
        return test_id, test_fn

    def _test_rule(
        self,
        rule_name: str,
        rule_op_class: Type[RuleOp],
        test: RuleTest,
        test_id: str,
        test_mode: Literal["valid", "invalid"],
    ) -> str | None:
        # Note, the rule's code cannot and should not depend
        # on the currently configured severity.
        # There is also no way for a rule to obtain the severity.
        severity = SEVERITY_ERROR
        linter = Linter(self._config, self._config_props)
        result = linter.validate(
            test.dataset,
            plugins={
                _PLUGIN_NAME: (
                    new_plugin(
                        name=_PLUGIN_NAME,
                        rules={
                            rule_name: Rule(
                                meta=RuleMeta(name=rule_name),
                                op_class=rule_op_class,
                            )
                        },
                    )
                )
            },
            rules={
                f"{_PLUGIN_NAME}/{rule_name}": (
                    [severity, *(test.args or ()), (test.kwargs or {})]
                    if test.args or test.kwargs
                    else severity
                )
            },
        )

        result_message_count = len(result.messages)

        expected = test.expected
        expected_message_count = 0
        expected_messages = None

        if test_mode == "valid":
            assert expected is None, (
                f"{test_id}: you cannot provide the keyword argument"
                f" `expected` for a RuleTest in 'valid' mode."
            )
        else:
            if isinstance(expected, int):
                expected_message_count = max(1, expected)
                expected_messages = None
            elif isinstance(expected, list):
                expected_message_count = len(expected)
                expected_messages = expected
            assert expected_message_count > 0, (
                f"{test_id}: you must provide a valid keyword argument"
                f" `expected` for a RuleTest in 'invalid' mode. Pass a list"
                f" of expected message or str objects or an int specifying"
                f" the expected number of messages."
            )

        lines: list[str] = []
        if result_message_count == expected_message_count:
            if expected_messages is None:
                return None
            all_ok = True
            texts = map(_get_message_text, expected_messages)
            result_texts = map(_get_message_text, result.messages)
            for i, (expected_text, result_text) in enumerate(zip(texts, result_texts)):
                if expected_text != result_text:
                    all_ok = False
                    lines.append(f"Message {i}:")
                    lines.append(f"  Expected: {expected_text}")
                    lines.append(f"  Actual: {result_text}")
            if all_ok:
                return None

        else:
            if expected_messages:
                lines.append(
                    f"Expected {format_item(expected_message_count, 'message')}:"
                )
                for i, text in enumerate(map(_get_message_text, expected_messages)):
                    lines.append(f"  {i}: {text}")
            if result.messages:
                lines.append(f"Actual {format_item(result_message_count, 'message')}:")
                for i, text in enumerate(map(_get_message_text, result.messages)):
                    lines.append(f"  {i}: {text}")

        result_text = format_problems(result.error_count, result.warning_count)
        if expected_message_count == result_message_count:
            problem_text = (
                f"got {result_text} as expected, but encountered message mismatch"
            )
        else:
            expected_text = format_count(expected_message_count, "problem")
            problem_text = f"expected {expected_text}, but got {result_text}"

        messages_text = "\n".join(lines)
        messages_text = (":\n" + messages_text) if messages_text else "."
        return f"Rule {rule_name!r}: {test_id}: {problem_text}{messages_text}"


def _format_test_id(
    test: RuleTest, test_index: int, test_mode: Literal["valid", "invalid"]
) -> str:
    if test.name:
        return f"test_{test_mode}_{to_snake_case(test.name)}"
    else:
        return f"test_{test_mode}_{test_index}"


def _get_message_text(m: Message | str) -> str:
    return m if isinstance(m, str) else m.message
