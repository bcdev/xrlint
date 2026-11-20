"""Build or preview the documentation, including its generated rule reference."""

import argparse
import subprocess
import sys
import time
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[2]
GENERATOR = Path(__file__).resolve().with_name("mkruleref.py")


def rule_sources():
    """Snapshot sources, including additions and removals, without watching output."""
    paths = [GENERATOR, PROJECT_DIR / "pyproject.toml"]
    paths.extend((PROJECT_DIR / "xrlint").rglob("*.py"))
    sources = {}
    for path in paths:
        try:
            stat = path.stat()
        except FileNotFoundError:
            # Editors may replace or remove a file while we scan the tree.
            continue
        sources[path] = (stat.st_mtime_ns, stat.st_size)
    return sources


def generate_rule_reference():
    # A fresh interpreter reloads plugin metadata instead of reusing imported modules.
    subprocess.run([sys.executable, str(GENERATOR)], cwd=PROJECT_DIR, check=True)


def serve(arguments):
    previous = rule_sources()
    generate_rule_reference()
    process = subprocess.Popen(
        [sys.executable, "-m", "zensical", "serve", *arguments], cwd=PROJECT_DIR
    )
    try:
        while process.poll() is None:
            time.sleep(0.5)
            current = rule_sources()
            if current != previous:
                previous = current
                try:
                    generate_rule_reference()
                except subprocess.CalledProcessError:
                    print(
                        "Rule reference generation failed; fix the sources to retry.",
                        file=sys.stderr,
                        flush=True,
                    )
        return process.returncode
    except KeyboardInterrupt:
        return 0
    finally:
        if process.poll() is None:
            process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["build", "serve"])
    options, arguments = parser.parse_known_args()
    subprocess.run(
        [sys.executable, str(GENERATOR.with_name("download_fonts.py"))],
        cwd=PROJECT_DIR,
        check=True,
    )
    if options.command == "serve":
        return serve(arguments)
    generate_rule_reference()
    return subprocess.call(
        [sys.executable, "-m", "zensical", "build", *arguments], cwd=PROJECT_DIR
    )


if __name__ == "__main__":
    sys.exit(main())
