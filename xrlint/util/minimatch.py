import re
from functools import cached_property
from typing import Literal


def minimatch(path: str, pattern: str) -> bool:
    """Match a file system path or URI against a
    [minimatch](https://github.com/isaacs/minimatch) pattern.

    Args:
        path: File system path or URI
        pattern: Minimatch pattern.
    Returns:
        `True` if `path` matches `pattern`.
    """
    matcher = Minimatcher(pattern)
    return matcher.match(path)


class Minimatcher:
    def __init__(self, pattern: str):
        self._pattern = pattern
        self._empty = False
        self._comment = False
        self._negate = False
        self._dir: Literal[True, None] = None

        if not pattern:
            self._empty = True
        else:
            if pattern[0] == "#":
                self._comment = True
                pattern = pattern[1:]
            elif pattern[0] == "!":
                self._negate = True
                pattern = pattern[1:]
                while pattern and pattern[0] == "!":
                    self._negate = not self._negate
                    pattern = pattern[1:]
            while pattern and pattern[-1] == "/":
                self._dir = True
                pattern = pattern[:-1]
        self.__pattern = pattern

    @property
    def pattern(self) -> str:
        return self._pattern

    @property
    def empty(self) -> bool:
        return self._empty

    @property
    def comment(self) -> bool:
        return self._comment

    @property
    def negate(self) -> bool:
        return self._negate

    @property
    def dir(self) -> Literal[True, None]:
        return self._dir

    @cached_property
    def _regex(self) -> re.Pattern:
        return _translate_to_regex(self.__pattern)

    def match(self, path: str) -> bool:
        if self._empty:
            return True
        if self._comment:
            return False

        while path and (path[-1] == "/" or path[-1] == "\\"):
            _dir = True
            path = path[:-1]

        match_result = self._regex.match(path)
        if self._negate:
            return match_result is None
        else:
            return match_result is not None


def _translate_to_regex(pattern: str) -> re.Pattern:
    """Translate the given
    [minimatch](https://github.com/isaacs/minimatch) pattern
    into a regex pattern.
    """
    # Escape all regex special characters except for * and ?
    pattern = re.escape(pattern)

    # Replace the escaped * and ? with their regex equivalents
    pattern = (
        pattern.replace(r"\*\*/", ".*/?")
        .replace(r"\*\*", ".*")
        .replace(r"\*", "[^/]*")
        .replace(r"\?", ".")
    )

    # Allow for trailing slashes, but don't force
    pattern = f"{pattern}/?"

    # Add start and end anchors to the pattern
    pattern = f"^{pattern}$"

    # Compile the pattern into a regex object
    return re.compile(pattern)
