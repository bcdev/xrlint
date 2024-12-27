from pathlib import Path
from typing import Any

import xarray as xr

from xrlint.config import Config
from xrlint.config import merge_configs
from xrlint.rule_reg import RuleRegistry
from xrlint.rule import Rule, RuleConfig, RuleOp
from xrlint.result import Result

# noinspection PyProtectedMember
from xrlint._linter.rule_ctx_impl import RuleContextImpl

# noinspection PyProtectedMember
from xrlint._linter.verify_impl import verify_dataset


class Linter:

    def __init__(
        self,
        _registry: RuleRegistry | None = None,
        config: Config | dict[str, Any] | None = None,
        **config_kwargs,
    ):
        if _registry is None:
            from xrlint.rules import import_rules

            _registry = import_rules()
        self._config = merge_configs(config, config_kwargs)
        self._registry = _registry

    def verify_dataset(
        self,
        dataset: str | Path | xr.Dataset,
        *,
        file_path: str | None = None,
        config: Config | dict[str, Any] | None = None,
        **config_kwargs,
    ) -> Result:
        config = merge_configs(self._config, config)
        config = merge_configs(config, config_kwargs)

        error: Exception | None = None
        if not isinstance(dataset, xr.Dataset):
            ds_source = dataset
            dataset, error = open_dataset(ds_source, config.opener_options or {})
            if not file_path and isinstance(ds_source, (str, Path)):
                file_path = f"{ds_source}"

        context = RuleContextImpl(
            config,
            dataset=dataset,
            file_path=file_path,
        )

        if error:
            context.report(f"{error}", fatal=True)
        else:
            rules = config.rules or {}
            for rule_id, rule_config in rules.items():
                with context.use_state(rule_id=rule_id):
                    self._apply_rule(context, rule_id, rule_config)

        return Result.new(file_path=context.file_path, messages=context.messages)

    def _apply_rule(
        self,
        context: RuleContextImpl,
        rule_id: str,
        rule_config: RuleConfig,
    ):
        rule = self._registry.lookup(rule_id)
        if rule is None:
            context.report(f"unknown rule", fatal=True)
            return

        if rule_config.severity == 0:
            # rule is off
            return

        with context.use_state(severity=rule_config.severity):
            # noinspection PyArgumentList
            verifier: RuleOp = rule.op_class(*rule_config.args, **rule_config.kwargs)
            verify_dataset(verifier, context)


def open_dataset(
    source: str, opener_options: dict[str, Any] | None
) -> tuple[xr.Dataset, None] | tuple[None, Exception]:
    try:
        return xr.open_dataset(source, **(opener_options or {})), None
    except (OSError, TypeError, ValueError) as e:
        return None, e


def _parse_rule_config(_rule: Rule, rule_spec: Any) -> RuleConfig:
    rule_config = RuleConfig.from_value(rule_spec)
    # TODO: validate options against rule.meta.schema
    return rule_config
