DEFAULT_OUTPUT_FORMAT = "simple"
DEFAULT_MAX_WARNINGS = -1

CONFIG_EXTENSIONS = ".yml", ".yaml", ".json", ".py"

DEFAULT_CONFIG_BASENAME = "xrlintrc"
DEFAULT_CONFIG_FILENAMES = [
    f".xrlintrc.yaml",
    f".xrlintrc.json",
    f"xrlintrc.py",  # no dot, because filename must be a valid module name
]
