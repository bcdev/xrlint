#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

from typing import Final

DEFAULT_CONFIG_BASENAME: Final = "xrlint_config"

DEFAULT_CONFIG_FILE_YAML: Final = f"{DEFAULT_CONFIG_BASENAME}.yaml"
DEFAULT_CONFIG_FILE_JSON: Final = f"{DEFAULT_CONFIG_BASENAME}.json"
DEFAULT_CONFIG_FILE_PY: Final = f"{DEFAULT_CONFIG_BASENAME}.py"

DEFAULT_CONFIG_FILES: Final = [
    DEFAULT_CONFIG_FILE_YAML,
    DEFAULT_CONFIG_FILE_JSON,
    DEFAULT_CONFIG_FILE_PY,
]

DEFAULT_OUTPUT_FORMAT: Final = "simple"
DEFAULT_MAX_WARNINGS: Final = 5

INIT_CONFIG_YAML: Final = "- recommended\n"

DEFAULT_GLOBAL_FILES: Final = ["**/*.zarr", "**/*.nc"]
DEFAULT_GLOBAL_IGNORES: Final = [".git", "node_modules"]
