from xrlint.plugins.core.rules.coords_for_dims import CoordsForDims

import xarray as xr

from xrlint.testing import RuleTest, RuleTester

valid_dataset_1 = xr.Dataset(attrs=dict(title="empty"))
valid_dataset_2 = xr.Dataset(
    attrs=dict(title="v-data"),
    coords={"x": xr.DataArray([0, 0.1, 0.2], dims="x", attrs={"units": "s"})},
    data_vars={"v": xr.DataArray([10, 20, 30], dims="x", attrs={"units": "m/s"})},
)
invalid_dataset_2 = valid_dataset_2.drop_vars("x")


CoordsForDimsTest = RuleTester.define_test(
    "coords-for-dims",
    CoordsForDims,
    valid=[
        RuleTest(dataset=valid_dataset_1),
        RuleTest(dataset=valid_dataset_2),
    ],
    invalid=[
        RuleTest(dataset=invalid_dataset_2),
    ],
)
