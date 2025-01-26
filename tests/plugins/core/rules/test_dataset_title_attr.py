import xarray as xr

from xrlint.plugins.core.rules.dataset_title_attr import DatasetTitleAttr
from xrlint.testing import RuleTest, RuleTester

valid_dataset_1 = xr.Dataset(attrs=dict(title="OC-Climatology"))
valid_dataset_2 = xr.Dataset(attrs=dict(title="SST-Climatology"))
invalid_dataset_1 = xr.Dataset()
invalid_dataset_2 = xr.Dataset(attrs=dict(title=""))


DatasetTitleAttrTest = RuleTester.define_test(
    "dataset-title-attr",
    DatasetTitleAttr,
    valid=[
        RuleTest(dataset=valid_dataset_1),
        RuleTest(dataset=valid_dataset_2),
    ],
    invalid=[
        RuleTest(dataset=invalid_dataset_1, expected=1),
        RuleTest(dataset=invalid_dataset_2, expected=1),
    ],
)
