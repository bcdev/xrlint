SEVERITY_ERROR = 2
SEVERITY_WARN = 1
SEVERITY_OFF = 0

SEVERITY_NAME_TO_CODE = {
    "error": SEVERITY_ERROR,
    "warn": SEVERITY_WARN,
    "off": SEVERITY_OFF,
}
SEVERITY_CODE_TO_NAME = {v: k for k, v in SEVERITY_NAME_TO_CODE.items()}

SEVERITY_ENUM: dict[int | str, int] = SEVERITY_NAME_TO_CODE | {
    v: v for v in SEVERITY_NAME_TO_CODE.values()
}
SEVERITY_ENUM_TEXT = ", ".join(f"{k!r}" for k in SEVERITY_ENUM.keys())

MISSING_DATASET_FILE_PATH = "<dataset>"

CORE_PLUGIN_NAME = "__core__"
