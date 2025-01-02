from contextlib import contextmanager
import os


@contextmanager
def text_file(file_path: str, content: str):
    with open(file_path, mode="w") as f:
        f.write(content)
    try:
        yield file_path
    finally:
        os.remove(file_path)
