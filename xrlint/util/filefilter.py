from dataclasses import dataclass

from xrlint.util.filepattern import FilePattern


@dataclass(frozen=True)
class FileFilter:
    """Encapsulates the file filtering mechanism using `files` and `ignores`.

    Args:
        files: File path patterns for files to be included.
        ignores: File path patterns for files to be excluded.
    """

    files: tuple[FilePattern, ...] = ()
    ignores: tuple[FilePattern, ...] = ()

    @classmethod
    def from_patterns(
        cls, files: list[str] | None, ignores: list[str] | None
    ) -> "FileFilter":
        return FileFilter(
            cls.patterns_to_matchers(files),
            cls.patterns_to_matchers(ignores, flip_negate=True),
        )

    @classmethod
    def patterns_to_matchers(
        cls, patterns: list[str] | None, flip_negate: bool = False
    ) -> tuple[FilePattern, ...]:
        matchers = (FilePattern(p, flip_negate=flip_negate) for p in patterns or ())
        return tuple(m for m in matchers if not (m.empty or m.comment))

    @property
    def empty(self) -> bool:
        return not (self.files or self.ignores)

    def merge(self, file_filter: "FileFilter") -> "FileFilter":
        return FileFilter(
            self.files + file_filter.files,  # note, we should exclude duplicates
            self.ignores + file_filter.ignores,
        )

    def accept(self, file_path) -> bool:
        included = False
        for m in self.files:
            if m.match(file_path):
                included = True
                break
        if not included:
            return False

        excluded = False
        for m in self.ignores:
            if not m.negate:
                if excluded:
                    # Already excluded, no need to check further
                    return False
                excluded = m.match(file_path)
            else:
                if excluded and m.match(file_path):
                    # Negate the old excluded status on match
                    excluded = False

        return not excluded
