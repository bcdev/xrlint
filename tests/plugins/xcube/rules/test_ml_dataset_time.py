#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

import xarray as xr

from tests.plugins.xcube.helpers import make_cube_levels
from xrlint.plugins.xcube.rules.ml_dataset_time import MLDatasetTime
from xrlint.plugins.xcube.util import LevelsMeta
from xrlint.testing import RuleTest, RuleTester

meta = LevelsMeta(
    version="1.0",
    num_levels=4,
    use_saved_levels=True,
    agg_methods={"chl": "mean"},
)
levels_with_time = make_cube_levels(4, 720, 360, nt=6, meta=meta)
levels_wo_time = make_cube_levels(4, 720, 360, meta=meta)

valid_dataset_0 = levels_with_time[0]
valid_dataset_1 = levels_with_time[1]
valid_dataset_2 = levels_wo_time[0]
valid_dataset_3 = xr.Dataset()

invalid_dataset_0 = levels_with_time[0].copy()
invalid_dataset_0["chl"] = invalid_dataset_0["chl"].chunk(time=3)

MLDatasetTimeTest = RuleTester.define_test(
    "ml-dataset-time",
    MLDatasetTime,
    valid=[
        RuleTest(dataset=valid_dataset_0),
        RuleTest(dataset=valid_dataset_1),
        RuleTest(dataset=valid_dataset_2),
        RuleTest(dataset=valid_dataset_3),
    ],
    invalid=[
        RuleTest(dataset=invalid_dataset_0, expected=1),
    ],
)
