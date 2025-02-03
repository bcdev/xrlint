#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

import xarray as xr

from tests.plugins.xcube.helpers import make_cube_levels
from xrlint.plugins.xcube.rules.ml_dataset_xy import MLDatasetXY
from xrlint.plugins.xcube.util import LevelsMeta, get_dataset_level_info
from xrlint.testing import RuleTest, RuleTester

meta = LevelsMeta(
    version="1.0",
    num_levels=4,
    use_saved_levels=True,
    agg_methods={"chl": "mean"},
)
levels = make_cube_levels(4, 720, 360, nt=3, meta=meta)

valid_dataset_0 = levels[0]
valid_dataset_1 = levels[1]
valid_dataset_2 = levels[2]
valid_dataset_3 = levels[3]
valid_dataset_4 = xr.Dataset()

levels = make_cube_levels(4, 720, 360, meta=meta)
valid_dataset_5 = levels[2]
level_info = get_dataset_level_info(valid_dataset_5)
for ds, _ in level_info.datasets:
    # remove spatial vars
    del ds["chl"]

levels = make_cube_levels(4, 720, 360, meta=meta)
invalid_dataset_0 = levels[2].copy()
# simulate resolution mismatch by exchanging 2 levels
level_info = get_dataset_level_info(invalid_dataset_0)
level_datasets = level_info.datasets
level_0_dataset = level_datasets[0]
level_1_dataset = level_datasets[1]
level_info.datasets[0] = level_1_dataset
level_info.datasets[1] = level_0_dataset


MLDatasetXYTest = RuleTester.define_test(
    "ml-dataset-xy",
    MLDatasetXY,
    valid=[
        RuleTest(dataset=valid_dataset_0),
        RuleTest(dataset=valid_dataset_1),
        RuleTest(dataset=valid_dataset_2),
        RuleTest(dataset=valid_dataset_3),
        RuleTest(dataset=valid_dataset_4),
        RuleTest(dataset=valid_dataset_5),
    ],
    invalid=[
        RuleTest(dataset=invalid_dataset_0, expected=2),
    ],
)
