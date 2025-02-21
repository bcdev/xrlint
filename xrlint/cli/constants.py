#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

from typing import Final


_MODULE_BASENAME: Final = "xrlint_config"
_REGULAR_BASENAME: Final = "xrlint-config"


DEFAULT_CONFIG_FILES: Final = [
    # Added in 0.5.1:
    f"{_REGULAR_BASENAME}.yaml",
    f"{_REGULAR_BASENAME}.yml",
    f"{_REGULAR_BASENAME}.json",
    # Until 0.5.0:
    f"{_MODULE_BASENAME}.yaml",
    f"{_MODULE_BASENAME}.yml",
    f"{_MODULE_BASENAME}.json",
    f"{_MODULE_BASENAME}.py",
]

DEFAULT_CONFIG_FILE_YAML: Final = f"{_REGULAR_BASENAME}.yaml"
DEFAULT_OUTPUT_FORMAT: Final = "simple"
DEFAULT_MAX_WARNINGS: Final = 5

INIT_CONFIG_YAML: Final = (
    "# XRLint configuration file\n"
    "# See https://bcdev.github.io/xrlint/config/\n"
    "\n"
    "- recommended\n"
)

DEFAULT_GLOBAL_FILES: Final = ["**/*.zarr", "**/*.nc"]
DEFAULT_GLOBAL_IGNORES: Final = [".git", "node_modules"]
