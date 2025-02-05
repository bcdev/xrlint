#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

from typing import Final

CORE_PLUGIN_NAME: Final = "__core__"
CORE_DOCS_URL = "https://bcdev.github.io/xrlint/rule-ref"

DATATREE_ROOT_NAME: Final = "dt"
DATASET_ROOT_NAME: Final = "ds"
MISSING_DATATREE_FILE_PATH: Final = "<datatree>"
MISSING_DATASET_FILE_PATH: Final = "<dataset>"

SEVERITY_ERROR: Final = 2
SEVERITY_WARN: Final = 1
SEVERITY_OFF: Final = 0

SEVERITY_NAME_TO_CODE: Final = {
    "error": SEVERITY_ERROR,
    "warn": SEVERITY_WARN,
    "off": SEVERITY_OFF,
}
SEVERITY_CODE_TO_NAME: Final = {v: k for k, v in SEVERITY_NAME_TO_CODE.items()}
SEVERITY_CODE_TO_CODE: Final = {v: v for v in SEVERITY_NAME_TO_CODE.values()}
SEVERITY_CODE_TO_COLOR = {2: "red", 1: "blue", 0: "green", None: ""}

SEVERITY_ENUM: Final[dict[int | str, int]] = (
    SEVERITY_NAME_TO_CODE | SEVERITY_CODE_TO_CODE
)
SEVERITY_ENUM_TEXT: Final = ", ".join(f"{k!r}" for k in SEVERITY_ENUM.keys())
