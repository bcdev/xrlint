#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

from xrlint.plugin import new_plugin
from xrlint.version import version

plugin = new_plugin(
    name="xcube",
    version=version,
    ref="xrlint.plugins.xcube:export_plugin",
    docs_url="https://xcube.readthedocs.io/en/latest/cubespec.html",
)
