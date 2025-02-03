#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

import importlib
import pathlib
from typing import Any, Callable, Type, TypeVar

from xrlint.util.formatting import format_message_type_of


def import_submodules(package_name: str, dry_run: bool = False) -> list[str]:
    package = importlib.import_module(package_name)
    assert hasattr(package, "__path__")

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
    module_ref: str,
    attr_ref: str | None = None,
    *,
    constant: bool = False,
    factory: Callable[[Any], T] | None = None,
    expected_type: Type[T] | None = None,
) -> tuple[T, str]:
    """Import an exported value from given module reference.

    Args:
        module_ref: Module reference. A string comprising either a fully
            qualified module name plus an optional attribute reference
            using format "<module-name>:<attr-ref>" or just a module name.
            In this case, `attr_ref` should be given.
            If it is not given, the module itself will be the exported value.
        attr_ref: Attribute reference. Should be given in the case where
            `module_ref` does not contain an attribute reference.
            Example values are "export_plugin", "export_config".
        constant: If `True` the value is expected to be a constant.
            If `False`, the default, the referenced attribute can
            be a no-arg callable that yields the actual exported value.
        factory: 1-arg factory function that converts a value of unknown
            type into `T`. Optional.
        expected_type: The expected value type that is a `T`. Optional.

    Returns:
        value: The imported value of type `T`.
        value_ref: The reference from which the value was imported.

    Raises:
        ValueImportError: if the value could not be imported
    """
    if ":" in module_ref:
        module_name, attr_ref = module_ref.rsplit(":", maxsplit=1)
    else:
        module_name = module_ref
        if attr_ref:
            module_ref = f"{module_name}:{attr_ref}"

    try:
        module = importlib.import_module(module_name)
    except ImportError as e:
        raise ValueImportError(
            f"failed to import value from {module_ref!r}: {e}"
        ) from e

    attr_value = module
    if attr_ref:
        attr_names = attr_ref.split(".")
        for i, attr_name in enumerate(attr_names):
            try:
                attr_value = getattr(attr_value, attr_name)
            except AttributeError:
                raise ValueImportError(
                    f"attribute {'.'.join(attr_names[: i + 1])!r}"
                    f" not found in module {module_name!r}"
                )

    should_invoke = not constant and callable(attr_value)
    if should_invoke:
        # We don't catch exceptions here,
        # because they occur in user land.
        # noinspection PyCallingNonCallable
        exported_value = attr_value()
    else:
        exported_value = attr_value

    if factory is not None:
        try:
            exported_value = factory(exported_value)
        except (ValueError, TypeError) as e:
            raise ValueImportError(
                f"failed converting value of {module_ref!r}: {e}"
            ) from e

    if expected_type is not None and not isinstance(exported_value, expected_type):
        raise ValueImportError(
            format_message_type_of(
                f"value of {module_ref}{('()' if should_invoke else '')}",
                exported_value,
                expected_type,
            )
        )

    return exported_value, module_ref


class ValueImportError(ImportError):
    """Special error that is raised while
    importing an exported value.
    """
