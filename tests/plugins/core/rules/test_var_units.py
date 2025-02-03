#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

import xarray as xr

from xrlint.plugins.core.rules.var_units import VarUnits
from xrlint.testing import RuleTest, RuleTester

valid_dataset_0 = xr.Dataset()
valid_dataset_1 = xr.Dataset(
    attrs=dict(title="v-data"),
    coords={"t": xr.DataArray([0, 1, 2], dims="t", attrs={"units": "seconds"})},
    data_vars={"v": xr.DataArray([10, 20, 30], dims="t", attrs={"units": "m/s"})},
)
valid_dataset_2 = valid_dataset_1.copy()
valid_dataset_2.t.encoding["units"] = "seconds since 2025-02-01 12:15:00"
del valid_dataset_2.t.attrs["units"]

valid_dataset_3 = valid_dataset_1.copy()
valid_dataset_3.t.attrs["grid_mapping_name"] = "latitude_longitude"

invalid_dataset_0 = valid_dataset_1.copy()
invalid_dataset_0.t.attrs = {}

invalid_dataset_1 = valid_dataset_1.copy()
invalid_dataset_1.t.attrs = {"units": 1}

invalid_dataset_2 = valid_dataset_1.copy()
invalid_dataset_2.t.attrs = {"units": ""}


VarUnitsTest = RuleTester.define_test(
    "var-units",
    VarUnits,
    valid=[
        RuleTest(dataset=valid_dataset_0),
        RuleTest(dataset=valid_dataset_1),
        RuleTest(dataset=valid_dataset_2),
        RuleTest(dataset=valid_dataset_3),
    ],
    invalid=[
        RuleTest(dataset=invalid_dataset_0, expected=["Missing attribute 'units'."]),
        RuleTest(dataset=invalid_dataset_1, expected=["Invalid attribute 'units': 1"]),
        RuleTest(dataset=invalid_dataset_2, expected=["Empty attribute 'units'."]),
    ],
)
