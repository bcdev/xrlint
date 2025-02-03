#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

import xarray as xr

from tests.plugins.xcube.helpers import make_cube
from xrlint.plugins.xcube.rules.no_chunked_coords import NoChunkedCoords
from xrlint.testing import RuleTest, RuleTester

valid_dataset_0 = xr.Dataset(attrs=dict(title="Empty"))
valid_dataset_1 = make_cube(360, 180, 3)
valid_dataset_2 = make_cube(90, 45, 20)
# ok, below default limit 5: ceil(20 / 5) = 4
valid_dataset_2.time.encoding["chunks"] = [4]

invalid_dataset_0 = make_cube(90, 45, 10)
# exceed default limit 5: ceil(10 / 1) = 10
invalid_dataset_0.time.encoding["chunks"] = [1]

NoChunkedCoordsTest = RuleTester.define_test(
    "no-chunked-coords",
    NoChunkedCoords,
    valid=[
        RuleTest(dataset=valid_dataset_0),
        RuleTest(dataset=valid_dataset_1),
        RuleTest(dataset=valid_dataset_2),
    ],
    invalid=[
        RuleTest(dataset=invalid_dataset_0, expected=1),
    ],
)
