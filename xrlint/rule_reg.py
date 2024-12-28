from inspect import isclass
from typing import Any, Callable, Literal, Type

from xrlint.rule import Rule, RuleMeta, RuleOp
from xrlint.util.naming import to_kebab_case
from xrlint.util.registry import Registry


class RuleRegistry(Registry[Rule]):
    # noinspection PyShadowingBuiltins
    def define_rule(
        self,
        name: str | None = None,
        version: str | None = None,
        schema: dict[str, Any] | list[dict[str, Any]] | bool | None = None,
        type: Literal["problem", "suggestion"] | None = None,
        description: str | None = None,
        docs_url: str | None = None,
        op_class: Type[RuleOp] | None = None,
    ) -> Callable[[Any], Type[RuleOp]] | None:
        def _register_rule(_op_class: Any) -> Type[RuleOp]:
            if not isclass(_op_class) or not issubclass(_op_class, RuleOp):
                raise TypeError(
                    f"component decorated by define_rule()"
                    f" must be a subclass of {RuleOp.__name__}"
                )
            meta = RuleMeta(
                name=name or to_kebab_case(_op_class.__name__),
                version=version,
                description=description,
                docs_url=docs_url,
                type=type if type is not None else "problem",
                schema=schema,
            )
            self.register(
                meta.name,
                Rule(
                    meta=meta,
                    op_class=_op_class,
                ),
            )
            return _op_class

        if op_class is None:
            # decorator case
            return _register_rule

        _register_rule(op_class)
