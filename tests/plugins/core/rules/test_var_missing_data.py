#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).
import numpy as np
import xarray as xr

from xrlint.plugins.core.rules.var_missing_data import VarMissingData
from xrlint.testing import RuleTest, RuleTester

valid_dataset_0 = xr.Dataset()
valid_dataset_1 = xr.Dataset(
    attrs=dict(title="v-data"),
    coords={"t": xr.DataArray([0, 1, 2], dims="t", attrs={"units": "seconds"})},
    data_vars={"v": xr.DataArray([10, 20, 30], dims="t", attrs={"units": "m/s"})},
)

invalid_dataset_0 = valid_dataset_1.copy(deep=True)
invalid_dataset_0.t.attrs["_FillValue"] = -999

invalid_dataset_1 = valid_dataset_1.copy(deep=True)
invalid_dataset_1.t.encoding["_FillValue"] = -999

invalid_dataset_2 = valid_dataset_1.copy(deep=True)
invalid_dataset_2.v.attrs["scaling_factor"] = 0.01

invalid_dataset_3 = valid_dataset_1.copy(deep=True)
invalid_dataset_3.v.encoding["dtype"] = np.dtype(np.float64)

invalid_dataset_4 = valid_dataset_1.copy(deep=True)
invalid_dataset_4.v.attrs["valid_range"] = [0, 1]

VarMissingDataTest = RuleTester.define_test(
    "var-missing-data",
    VarMissingData,
    valid=[
        RuleTest(dataset=valid_dataset_0),
        RuleTest(dataset=valid_dataset_1),
    ],
    invalid=[
        RuleTest(
            dataset=invalid_dataset_0,
            expected=[
                "Unexpected attribute '_FillValue', coordinates must not have missing data."
            ],
        ),
        RuleTest(
            dataset=invalid_dataset_1,
            expected=[
                "Unexpected encoding '_FillValue', coordinates must not have missing data."
            ],
        ),
        RuleTest(
            dataset=invalid_dataset_2,
            expected=["Missing attribute '_FillValue' since data packing is used."],
        ),
        RuleTest(
            dataset=invalid_dataset_3,
            expected=["Missing attribute '_FillValue', which should be NaN."],
        ),
        RuleTest(
            dataset=invalid_dataset_4,
            expected=["Valid ranges are not recognized by xarray (as of Feb 2025)."],
        ),
    ],
)
