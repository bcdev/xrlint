import importlib
import pathlib
from typing import Any

from xrlint.util.formatting import format_message_type_of

_UNDEFINED = object()


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


def import_value(
    module_name: str,
    attr_name: str,
    attr_type: type | tuple[type, ...],
    /,
    dir_path: str | None = None,
) -> Any:
    import importlib
    import sys

    old_path: list[str] | None = None
    if dir_path is not None:
        dir_path = dir_path or "."
        old_path = sys.path
        sys.path = [dir_path] + old_path

    try:
        config_module = importlib.import_module(module_name)
        attr_value = getattr(config_module, attr_name)
        if not isinstance(attr_value, attr_type):
            if callable(attr_value):
                attr_value = attr_value()
                if not isinstance(attr_value, attr_type):
                    raise TypeError(
                        format_message_type_of(
                            f"return value of {module_name}.{attr_name}()",
                            attr_value,
                            attr_type,
                        )
                    )
            else:
                raise TypeError(
                    format_message_type_of(
                        f"value of attribute {module_name}.{attr_name}",
                        attr_value,
                        attr_type,
                    )
                )
        return attr_value
    finally:
        if old_path is not None:
            sys.path = old_path
