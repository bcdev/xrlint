#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

from xrlint.plugins.xcube.rules.any_spatial_data_var import AnySpatialDataVar
from xrlint.testing import RuleTest, RuleTester

from .test_grid_mapping_naming import make_dataset

valid_dataset = make_dataset()
invalid_dataset = valid_dataset.drop_vars(["chl", "tsm"])


AnySpatialDataVarTest = RuleTester.define_test(
    "any-spatial-data-var",
    AnySpatialDataVar,
    valid=[
        RuleTest(dataset=valid_dataset),
    ],
    invalid=[
        RuleTest(dataset=invalid_dataset, expected=1),
    ],
)
