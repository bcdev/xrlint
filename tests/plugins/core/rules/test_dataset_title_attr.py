import xrlint.api as xrl
from xrlint.plugins.core.rules.dataset_title_attr import DatasetTitleAttr
import xarray as xr


valid_dataset_1 = xr.Dataset(attrs=dict(title="OC-Climatology"))
valid_dataset_2 = xr.Dataset(attrs=dict(title="SST-Climatology"))
invalid_dataset_1 = xr.Dataset()
invalid_dataset_2 = xr.Dataset(attrs=dict(title=""))


DatasetTitleAttrTest = xrl.RuleTester.define_test(
    "dataset-title-attr",
    DatasetTitleAttr,
    valid=[
        xrl.RuleTest(dataset=valid_dataset_1),
        xrl.RuleTest(dataset=valid_dataset_2),
    ],
    invalid=[
        xrl.RuleTest(dataset=invalid_dataset_1),
        xrl.RuleTest(dataset=invalid_dataset_2),
    ],
)
