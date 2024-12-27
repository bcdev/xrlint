from inspect import isclass
from typing import Any, Callable, Type

from xrlint.formatter import Formatter, FormatterMeta, FormatterOp
from xrlint.util.naming import to_kebab_case
from xrlint.util.registry import Registry


class FormatterRegistry(Registry[Formatter]):
    def define_formatter(
        self,
        name: str | None = None,
        version: str | None = None,
        schema: dict[str, Any] | list[dict[str, Any]] | bool | None = None,
    ) -> Callable[[Any], Type[FormatterOp]]:

        def decorator(op_class: Any) -> Type[FormatterOp]:
            if not isclass(op_class) or not issubclass(op_class, FormatterOp):
                raise TypeError(
                    f"component decorated by define_formatter()"
                    f" must be a subclass of {FormatterOp.__name__}"
                )
            meta = FormatterMeta(
                name=name or to_kebab_case(op_class.__name__),
                version=version,
                schema=schema,
            )
            self.register(meta.name, Formatter(meta=meta, op_class=op_class))
            return op_class

        return decorator
