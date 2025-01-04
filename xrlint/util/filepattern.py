import re
from functools import cached_property
from typing import Literal
import platform

_WIN_OS = platform.system() == "Windows"


class FilePattern:
    """A file path pattern that naively implements a subset
    of the [minimatch](https://github.com/isaacs/minimatch)
    pattern specification.

    It currently supports:

    * `?` single character
    * `*` anything except slashes
    * `**` anything including slashes ("glob-star")
    * `!<pattern>` negations
    * `#<comment>` comments

    The actual pattern matching is implemented with
    Python regular expressions.

    Args:
        pattern: A "minimatch" pattern.
        flip_negate: Returns from negate expressions the same as
            if they were not negated, i.e.,
            `True` on a hit, `False` on a miss.
    """

    def __init__(self, pattern: str, flip_negate: bool = False):
        self._pattern = pattern
        self._flip_negate = flip_negate

        self._empty = False
        self._comment = False
        self._negate = False
        self._dir: Literal[True, None] = None  # we cannot know

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
        """Original pattern."""
        return self._pattern

    @property
    def empty(self) -> bool:
        """`True` if this matcher's pattern is empty."""
        return self._empty

    @property
    def comment(self) -> bool:
        """`True` if this matcher's pattern is a comment."""
        return self._comment

    @property
    def negate(self) -> bool:
        """`True` if this matcher's pattern negates."""
        return self._negate

    @property
    def dir(self) -> Literal[True, None]:
        """`True` if this matcher's pattern denotes a directory."""
        return self._dir

    @cached_property
    def _regex(self) -> re.Pattern:
        return _translate_to_regex(self.__pattern)

    def __str__(self):
        return self.pattern

    def __repr__(self):
        return f"FilePattern({self.pattern!r})"

    def __eq__(self, other):
        if other is self:
            return True
        if not isinstance(other, FilePattern):
            return False
        return self.pattern == other.pattern

    def __neq__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.pattern)

    def match(self, path: str) -> bool:
        """Match a file system path or URI against this pattern.

        Args:
            path: File system path or URI
        Returns:
            `True` if `path` matches.
        """
        if self._empty:
            return True
        if self._comment:
            return False

        path = path if not _WIN_OS else path.replace("\\", "")
        while path and path[-1] == "/":
            path = path[:-1]

        match_result = self._regex.match(path)
        if self._negate and not self._flip_negate:
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
