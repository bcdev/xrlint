from collections.abc import Iterable
from dataclasses import dataclass

from xrlint.result import Result


@dataclass()
class Stats:
    """Utility to collect simple statistics from results."""

    error_count: int = 0
    warning_count: int = 0

    def collect(self, results: Iterable[Result]) -> Iterable[Result]:
        """Collect statistics from `results`."""
        for result in results:
            self.error_count += result.error_count
            self.warning_count += result.warning_count
            yield result
