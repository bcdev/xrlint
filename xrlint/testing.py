import unittest
from dataclasses import dataclass
from typing import Type, Callable, Literal, Any

import xarray as xr

from xrlint.constants import SEVERITY_ERROR
from xrlint.linter import Linter
from xrlint.plugin import Plugin
from xrlint.plugin import PluginMeta
from xrlint.result import Message
from xrlint.result import Result
from xrlint.rule import Rule
from xrlint.rule import RuleMeta
from xrlint.rule import RuleOp
from xrlint.util.naming import to_snake_case
from xrlint.util.formatting import format_problems


@dataclass(frozen=True, kw_only=True)
class RuleTest:
    """A rule test case."""

    dataset: xr.Dataset
    """The dataset to verify."""

    name: str | None = None
    """A name that helps identifying the test case."""

    args: tuple | list | None = None
    """Optional positional arguments passed to the rule verifier's constructor."""

    kwargs: dict[str, Any] | None = None
    """Optional keyword arguments passed to the rule verifier's constructor."""

    expected: list[Message] | int | None = 0
    """Expected messages.
    Either a list of expected message objects or
    the number of expected message.
    Must not be provided for valid checks
    and must be provided for invalid checks.
    """


class RuleTester:
    """Utility that helps to test rules.

    Args:
        config: optional xrlint configuration
    """

    def __init__(self, **config):
        self._config = config

    def run(
        self,
        rule_name: str,
        rule_verifier_class: Type[RuleOp],
        *,
        valid: list[RuleTest] | None = None,
        invalid: list[RuleTest] | None = None,
    ):
        """Run the given tests in `valid` and `invalid`
        against the given rule.

        Args:
            rule_name: the rule's name
            rule_verifier_class: the class derived from `RuleVerifier`
            valid: list of tests that expect no reported problems
            invalid: list of tests that expect reported problems

        Raises:
            AssertionError: if one of the checks fails
        """
        tests = self._create_tests(
            rule_name, rule_verifier_class, valid=valid, invalid=invalid
        )
        for test in tests.values():
            print(f"Rule {rule_name!r}: running {test.__name__}()...")
            # noinspection PyTypeChecker
            test(None)

    @classmethod
    def define_test(
        cls,
        rule_name: str,
        rule_verifier_class: Type[RuleOp],
        *,
        valid: list[RuleTest] | None = None,
        invalid: list[RuleTest] | None = None,
        config: dict[str, Any] | None = None,
    ) -> Type[unittest.TestCase]:
        """Create a `unittest.TestCase` class for the given rule and tests.

        The returned class is derived from `unittest.TestCase`
        and contains a test method for each of the tests in
        `valid` and `invalid`.

        Args:
            rule_name: the rule's name
            rule_verifier_class: the class derived from `RuleVerifier`
            valid: list of tests that expect no reported problems
            invalid: list of tests that expect reported problems
            config: optional xrlint configuration
        Returns:
            A new class derived from `unittest.TestCase`.
        """
        tester = RuleTester(**(config or {}))
        tests = tester._create_tests(
            rule_name, rule_verifier_class, valid=valid, invalid=invalid
        )
        # noinspection PyTypeChecker
        return type(f"{rule_verifier_class.__name__}Test", (unittest.TestCase,), tests)

    def _create_tests(
        self,
        rule_name: str,
        rule_verifier_class: Type[RuleOp],
        valid: list[RuleTest] | None,
        invalid: list[RuleTest] | None,
    ) -> dict[str, Callable[[unittest.TestCase | None], None]]:
        def make_args(tests: list[RuleTest] | None, mode: Literal["valid", "invalid"]):
            return [(test, index, mode) for index, test in enumerate(tests or [])]

        return dict(
            self._create_test(rule_name, rule_verifier_class, *args)
            for args in make_args(valid, "valid") + make_args(invalid, "invalid")
        )

    def _create_test(
        self,
        rule_name: str,
        rule_verifier_class: Type[RuleOp],
        test: RuleTest,
        test_index: int,
        test_mode: Literal["valid", "invalid"],
    ) -> tuple[str, Callable]:
        test_id = _format_test_id(test, test_index, test_mode)

        def test_fn(_self: unittest.TestCase):
            error_message = self._test_rule(
                rule_name, rule_verifier_class, test, test_id, test_mode
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
        linter = Linter(**self._config)
        result = linter.verify_dataset(
            test.dataset,
            plugins={
                "test": (
                    Plugin(
                        meta=PluginMeta(name="test"),
                        rules={
                            rule_name: Rule(
                                meta=RuleMeta(name=rule_name), op_class=rule_op_class
                            )
                        },
                    )
                )
            },
            rules={
                f"test/{rule_name}": (
                    [severity, *(test.args or ()), (test.kwargs or {})]
                    if test.args or test.kwargs
                    else severity
                )
            },
        )

        assert_ok = _assert_valid if test_mode == "valid" else _assert_invalid
        if assert_ok(result):
            return None
        else:
            return _format_error_message(rule_name, test_id, test_mode, result)


def _assert_valid(r: Result):
    return r.error_count == 0 and r.warning_count == 0


def _assert_invalid(r: Result):
    return r.error_count != 0 or r.warning_count != 0


def _format_error_message(
    rule_name: str,
    test_id: str,
    test_mode: Literal["valid", "invalid"],
    result: Result,
) -> str:
    actual = format_problems(result.error_count, result.warning_count)
    expected = f"{'no problem' if test_mode == 'valid' else 'one or more problems'}"
    return (
        f"Rule {rule_name!r}: {test_id}:"
        f" expected {expected}, but got {actual}:\n{result}"
    )


def _format_test_id(
    test: RuleTest, test_index: int, test_mode: Literal["valid", "invalid"]
) -> str:
    if test.name:
        return f"test_{test_mode}_{to_snake_case(test.name)!r}"
    else:
        return f"test_{test_mode}_{test_index}"
