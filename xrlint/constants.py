from typing import Final

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

SEVERITY_ENUM: Final[dict[int | str, int]] = (
    SEVERITY_NAME_TO_CODE | SEVERITY_CODE_TO_CODE
)
SEVERITY_ENUM_TEXT: Final = ", ".join(f"{k!r}" for k in SEVERITY_ENUM.keys())

MISSING_DATASET_FILE_PATH: Final = "<dataset>"

CORE_PLUGIN_NAME: Final = "__core__"
