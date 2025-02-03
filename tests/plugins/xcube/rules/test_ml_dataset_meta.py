#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

import xarray as xr

from tests.plugins.xcube.helpers import make_cube_levels
from xrlint.plugins.xcube.rules.ml_dataset_meta import MLDatasetMeta
from xrlint.plugins.xcube.util import (
    LevelInfo,
    LevelsMeta,
    get_dataset_level_info,
    set_dataset_level_info,
)
from xrlint.testing import RuleTest, RuleTester


def _replace_meta(dataset: xr.Dataset, meta: LevelsMeta) -> xr.Dataset:
    dataset = dataset.copy()
    old_level_info = get_dataset_level_info(dataset)
    new_level_info = LevelInfo(
        level=old_level_info.level,
        num_levels=old_level_info.num_levels,
        datasets=old_level_info.datasets,
        meta=meta,
    )
    set_dataset_level_info(dataset, new_level_info)
    return dataset


levels_with_meta = make_cube_levels(
    4,
    720,
    360,
    meta=LevelsMeta(
        version="1.0",
        num_levels=4,
        use_saved_levels=True,
        agg_methods={"chl": "mean"},
    ),
)

valid_dataset_0 = levels_with_meta[0]
valid_dataset_1 = levels_with_meta[1]
valid_dataset_2 = levels_with_meta[2]
valid_dataset_3 = xr.Dataset()

levels_wo_meta = make_cube_levels(4, 720, 360, force_infos=True)
invalid_dataset_0 = levels_wo_meta[0]
invalid_dataset_1 = _replace_meta(
    levels_wo_meta[0].copy(),
    meta=LevelsMeta(
        version="2.0",  # error: != "1.x"
        num_levels=0,  # error: < 1
        # error: missing use_saved_levels=False
        # error: missing agg_methods={"chl": "mean"}
    ),
)
invalid_dataset_2 = _replace_meta(
    levels_wo_meta[0],
    meta=LevelsMeta(
        version="1.0",  # ok
        num_levels=3,  # error: != level_info.num_levels
    ),
)

invalid_dataset_3 = _replace_meta(
    levels_wo_meta[0],
    meta=LevelsMeta(
        version="1.0",  # ok
        num_levels=4,  # ok
        use_saved_levels=False,  # ok
        agg_methods={"tsm": "median"},  # error: where is "chl"?
    ),
)

MLDatasetMetaTest = RuleTester.define_test(
    "ml-dataset-meta",
    MLDatasetMeta,
    valid=[
        RuleTest(dataset=valid_dataset_0),
        RuleTest(dataset=valid_dataset_1),
        RuleTest(dataset=valid_dataset_2),
        RuleTest(dataset=valid_dataset_3),
    ],
    invalid=[
        RuleTest(dataset=invalid_dataset_0, expected=1),
        RuleTest(dataset=invalid_dataset_1, expected=4),
        RuleTest(dataset=invalid_dataset_2, expected=3),
        RuleTest(dataset=invalid_dataset_3, expected=2),
    ],
)
