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


def import_value(
    module_name: str,
    function_name: str,
    factory: Callable[[Any], T],
) -> T:
    """Import an exported value from given module.

    Args:
        module_name: Module name.
        function_name: Name of the function used to provide
            the exported value, e.g., "export_plugin", "export_configs".
        factory:
            The 1-arg factory function that converts a value
            into T.
    Returns:
        The imported value of type T.
    Raises:
        ValueImportError: if the value could not be imported
    """
    config_module = importlib.import_module(module_name)

    try:
        export_function = getattr(config_module, function_name)
    except AttributeError:
        raise ValueImportError(f"missing {function_name}()")

    if not callable(export_function):
        raise ValueImportError(
            format_message_type_of(
                function_name,
                export_function,
                "function",
            )
        )

    exported_value = export_function()

    try:
        return factory(exported_value)
    except (ValueError, TypeError) as e:
        raise ValueImportError(f"return value of {function_name}(): {e}") from e


class ValueImportError(ImportError):
    """Special error that is raised while
    importing an exported value.
    """
