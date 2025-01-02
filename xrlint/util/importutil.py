import importlib
import pathlib
from typing import TypeVar, Callable, Any

from xrlint.util.formatting import format_message_type_of


def import_submodules(package_name: str, dry_run: bool = False) -> list[str]:

    package = importlib.import_module(package_name)
    if not hasattr(package, "__path__"):
        return []

    package_path = pathlib.Path(package.__path__[0])

    module_names = []
    for module_file in package_path.iterdir():
        if (
            module_file.is_file()
            and module_file.name.endswith(".py")
            and module_file.name != "__init__.py"
        ):
            module_names.append(module_file.name[:-3])
        elif (
            module_file.is_dir()
            and module_file.name != "__pycache__"
            and (module_file / "__init__.py").is_file()
        ):
            module_names.append(module_file.name)

    qual_module_names = [f"{package_name}.{m}" for m in module_names]

    if not dry_run:
        for qual_module_name in qual_module_names:
            importlib.import_module(qual_module_name)

    return qual_module_names


T = TypeVar("T")


def import_exported_value(
    module_name: str,
    export_item_name: str,
    factory: Callable[[Any], T],
) -> T:
    export_function_name = f"export_{export_item_name}"
    config_module = importlib.import_module(module_name)
    export_function = getattr(config_module, export_function_name)
    return eval_exported_value(export_function_name, export_function, factory)


def eval_exported_value(
    export_function_name: str, export_function: Any, factory: Callable[[Any], T]
) -> T:
    if not callable(export_function):
        raise TypeError(
            format_message_type_of(
                export_function_name,
                export_function,
                "function",
            )
        )

    try:
        export_value = export_function()
    except Exception as e:
        raise UserCodeException(f"while executing {export_function_name}(): {e}") from e

    try:
        return factory(export_value)
    except (ValueError, TypeError) as e:
        raise type(e)(
            f"return value of {export_function_name}(): {e}",
        )


class UserCodeException(Exception):
    """Special exception that is never caught in xrlint,
    so users can see the stacktrace into their code.
    """
