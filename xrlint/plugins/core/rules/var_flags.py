#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

from typing import Any

import numpy as np

from xrlint.node import VariableNode
from xrlint.plugins.core.plugin import plugin
from xrlint.rule import RuleContext, RuleOp

FLAG_MEANINGS = "flag_meanings"
FLAG_VALUES = "flag_values"
FLAG_MASKS = "flag_masks"


@plugin.define_rule(
    "var-flags",
    version="1.0.0",
    type="suggestion",
    description=(
        "Validate attributes 'flag_values', 'flag_masks' and 'flag_meanings'"
        " that make variables that contain flag values self describing. "
    ),
    docs_url="https://cfconventions.org/cf-conventions/cf-conventions.html#flags",
)
class VarFlags(RuleOp):
    def validate_variable(self, ctx: RuleContext, node: VariableNode):
        flag_values = node.array.attrs.get(FLAG_VALUES)
        flag_masks = node.array.attrs.get(FLAG_MASKS)
        flag_meanings = node.array.attrs.get(FLAG_MEANINGS)

        has_values = flag_values is not None
        has_masks = flag_masks is not None
        has_meanings = flag_meanings is not None

        flag_count: int | None = None

        if has_values:
            flag_count = _validate_flag_values(
                ctx,
                flag_values,
                has_meanings,
            )

        if has_masks:
            flag_count = _validate_flag_masks(
                ctx,
                flag_masks,
                has_meanings,
                flag_count,
            )

        if has_meanings:
            _validate_flag_meanings(
                ctx,
                flag_meanings,
                has_values,
                has_masks,
                flag_count,
            )

        if has_values and has_masks:
            _validate_variable(
                ctx,
                node.array.dtype,
            )


def _validate_flag_values(
    ctx: RuleContext, flag_values: Any, has_meanings: bool
) -> int | None:
    if not has_meanings:
        ctx.report(
            f"Missing attribute {FLAG_MEANINGS!r} to explain attribute {FLAG_VALUES!r}."
        )
    type_ok, flag_count = _check_values(flag_values)
    if not type_ok or flag_count is None:
        ctx.report(
            f"Attribute {FLAG_VALUES!r} must be a"
            " 1-d array of integers with length >= 1."
        )
    return flag_count


def _validate_flag_masks(
    ctx: RuleContext, flag_masks: Any, has_meanings: bool, flag_count: int | None
) -> int | None:
    if not has_meanings:
        ctx.report(
            f"Missing attribute {FLAG_MEANINGS!r} to explain attribute {FLAG_MASKS!r}"
        )
    type_ok, flag_masks_count = _check_values(flag_masks)
    if not type_ok or flag_masks_count is None:
        ctx.report(
            f"Attribute {FLAG_MASKS!r} must be a"
            " 1-d array of integers with length >= 1."
        )
    if flag_count is None:
        flag_count = flag_masks_count
    elif flag_masks_count is not None and flag_masks_count != flag_count:
        ctx.report(
            f"Attribute {FLAG_MASKS!r} must have same length"
            f" as attribute {FLAG_VALUES!r}."
        )
    return flag_count


def _validate_flag_meanings(
    ctx: RuleContext,
    flag_meanings: Any,
    has_values: bool,
    has_masks: bool,
    flag_count: int | None,
):
    if not has_values and not has_masks:
        ctx.report(
            f"Missing attribute {FLAG_VALUES!r} or {FLAG_MASKS!r}"
            f" when attribute {FLAG_MASKS!r} is used."
        )
    type_ok, flag_meanings_count = _check_meanings(flag_meanings)
    if not type_ok or flag_meanings_count is None:
        ctx.report(
            f"Attribute {FLAG_MASKS!r} must be a space-separated string"
            f" with at least two entries."
        )
    if (
        flag_meanings_count is not None
        and flag_count is not None
        and flag_meanings_count != flag_count
    ):
        ctx.report(
            f"Attribute {FLAG_MASKS!r} must have same length"
            f" as attributes {FLAG_VALUES!r} or {FLAG_MEANINGS!r}."
        )


def _validate_variable(ctx: RuleContext, var_dtype: np.dtype):
    if not np.issubdtype(var_dtype, np.integer):
        ctx.report(
            f"Flags variable should have an integer data type, was {var_dtype!r}"
        )


def _check_values(values: Any) -> tuple[bool, int | None]:
    if isinstance(values, (tuple, list)) or (
        isinstance(values, np.ndarray) and values.ndim == 1
    ):
        count = len(values)
        return all(isinstance(v, int) for v in values), count if count >= 1 else None
    return False, None


def _check_meanings(meanings: Any):
    if isinstance(meanings, str):
        meanings_list = [m.strip() for m in meanings.split(" ")]
        count = len(meanings_list)
        return True, count if count >= 1 else None
    return False, None
