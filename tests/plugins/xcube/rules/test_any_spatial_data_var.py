from xrlint.plugins.xcube.rules.any_spatial_data_var import AnySpatialDataVar
from .test_grid_mapping_naming import make_dataset

from xrlint.testing import RuleTester, RuleTest


valid_dataset = make_dataset()
invalid_dataset = valid_dataset.drop_vars(["chl", "tsm"])


AnySpatialDataVarTest = RuleTester.define_test(
    "any-spatial-data-var",
    AnySpatialDataVar,
    valid=[
        RuleTest(dataset=valid_dataset),
    ],
    invalid=[
        RuleTest(dataset=invalid_dataset),
    ],
)
