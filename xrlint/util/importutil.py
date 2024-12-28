import importlib
import pathlib
from typing import TypeVar, Type

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
    name: str,
    return_type: Type[T],
) -> T:
    config_module = importlib.import_module(module_name)
    export_name = f"export_{name}"
    export_function = getattr(config_module, export_name)
    if not callable(export_function):
        raise TypeError(
            format_message_type_of(
                f"{module_name}.{export_name}",
                export_function,
                "function",
            )
        )
    export_value = export_function()
    if not isinstance(export_value, return_type):
        raise TypeError(
            format_message_type_of(
                f"return value of {module_name}.{export_name}()",
                export_value,
                return_type,
            )
        )
    return export_value
