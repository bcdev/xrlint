#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

import os
from contextlib import contextmanager


@contextmanager
def text_file(file_path: str, content: str):
    with open(file_path, mode="w") as f:
        f.write(content)
    try:
        yield file_path
    finally:
        os.remove(file_path)
