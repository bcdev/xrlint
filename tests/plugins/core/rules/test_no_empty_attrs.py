from xrlint.plugins.core.rules.no_empty_attrs import NoEmptyAttrs

import xarray as xr

from xrlint.testing import RuleTest, RuleTester

valid_dataset_1 = xr.Dataset(attrs=dict(title="empty"))
valid_dataset_2 = xr.Dataset(
    attrs=dict(title="v-data"),
    coords={"x": xr.DataArray([0, 0.1, 0.2], dims="x", attrs={"units": "s"})},
    data_vars={"v": xr.DataArray([10, 20, 30], dims="x", attrs={"units": "m/s"})},
)
invalid_dataset_1 = valid_dataset_1.copy()
invalid_dataset_2 = valid_dataset_2.copy()
invalid_dataset_3 = valid_dataset_2.copy()
invalid_dataset_1.attrs = {}
invalid_dataset_2.x.attrs = {}
invalid_dataset_3.v.attrs = {}


NoEmptyAttrsTest = RuleTester.define_test(
    "no-empty-attrs",
    NoEmptyAttrs,
    valid=[
        RuleTest(dataset=valid_dataset_1),
        RuleTest(dataset=valid_dataset_2),
    ],
    invalid=[
        RuleTest(dataset=invalid_dataset_1),
        RuleTest(dataset=invalid_dataset_2),
        RuleTest(dataset=invalid_dataset_3),
    ],
)
