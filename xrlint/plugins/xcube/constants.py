#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

from typing import Final

LON_NAME: Final = "lon"
LAT_NAME: Final = "lat"
X_NAME: Final = "x"
Y_NAME: Final = "y"
TIME_NAME: Final = "time"

GM_NAMES: Final = "spatial_ref", "crs"
GM_NAMES_TEXT: Final = " or ".join(repr(gm_name) for gm_name in GM_NAMES)

ML_FILE_PATTERN: Final = "**/*.levels"
ML_META_FILENAME: Final = ".zlevels"
ML_INFO_ATTR: Final = "_LEVEL_INFO"
