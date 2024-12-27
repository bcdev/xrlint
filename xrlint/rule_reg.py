from inspect import isclass
from typing import Any, Callable, Literal, Type

from xrlint.rule import Rule, RuleMeta, RuleOp
from xrlint.util.naming import to_kebab_case
from xrlint.util.registry import Registry


class RuleRegistry(Registry[Rule]):
    def define_rule(
        self,
        name: str | None = None,
        version: str | None = None,
        schema: dict[str, Any] | list[dict[str, Any]] | bool | None = None,
        type: Literal["problem", "suggestion"] | None = None,
    ) -> Callable[[Any], Type[RuleOp]]:
        def decorator(verifier_class: Any) -> Type[RuleOp]:
            if not isclass(verifier_class) or not issubclass(verifier_class, RuleOp):
                raise TypeError(
                    f"component decorated by define_rule()"
                    f" must be a subclass of {RuleOp.__name__}"
                )
            meta = RuleMeta(
                name=name or to_kebab_case(verifier_class.__name__),
                version=version,
                type=type if type is not None else "problem",
                schema=schema,
            )
            self.register(
                meta.name,
                Rule(
                    meta=meta,
                    op_class=verifier_class,
                ),
            )
            return verifier_class

        return decorator
