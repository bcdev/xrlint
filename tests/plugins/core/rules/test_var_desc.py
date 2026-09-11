#  Copyright © 2025-2026 Brockmann Consult GmbH and contributors.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

import xarray as xr

from xrlint.plugins.core.rules.var_desc import VarDesc
from xrlint.testing import RuleTest, RuleTester

pressure_attrs = {
    "long_name": "mean sea level pressure",
    "units": "hPa",
    "standard_name": "air_pressure_at_sea_level",
}

time_coord = xr.DataArray(
    [1, 2, 3], dims="time", attrs={"units": "days since 2025-01-01"}
)

valid_dataset_0 = xr.Dataset(
    coords={"time": time_coord},
)
valid_dataset_1 = xr.Dataset(
    data_vars={"pressure": xr.DataArray([1, 2, 3], dims="time", attrs=pressure_attrs)},
    coords={"time": time_coord},
)
valid_dataset_2 = xr.Dataset(
    data_vars={
        "chl": xr.DataArray(
            [1, 2, 3], dims="time", attrs={"description": "It is air pressure"}
        )
    },
    coords={"time": time_coord},
)

invalid_dataset_0 = xr.Dataset(
    attrs={},
    data_vars={"chl": xr.DataArray([1, 2, 3], dims="time", attrs={})},
    coords={"time": time_coord},
)

invalid_dataset_1 = xr.Dataset(
    attrs={},
    data_vars={
        "chl": xr.DataArray(
            [1, 2, 3],
            dims="time",
            attrs={"standard_name": "air_pressure_at_sea_level"},
        )
    },
    coords={"time": time_coord},
)
invalid_dataset_2 = xr.Dataset(
    attrs={},
    data_vars={
        "chl": xr.DataArray(
            [1, 2, 3], dims="time", attrs={"long_name": "mean sea level pressure"}
        )
    },
    coords={"time": time_coord},
)
invalid_dataset_3 = xr.Dataset(
    attrs={},
    data_vars={"chl": xr.DataArray([1, 2, 3], dims="time", attrs=pressure_attrs)},
    coords={"time": time_coord},
)

VarDescTest = RuleTester.define_test(
    "var-desc",
    VarDesc,
    valid=[
        RuleTest(dataset=valid_dataset_0),
        RuleTest(dataset=valid_dataset_1),
        RuleTest(dataset=valid_dataset_2, kwargs={"attrs": ["description"]}),
    ],
    invalid=[
        RuleTest(
            dataset=invalid_dataset_0,
            expected=[
                "Missing attribute 'standard_name'.",
                "Missing attribute 'long_name'.",
            ],
        ),
        RuleTest(
            dataset=invalid_dataset_1, expected=["Missing attribute 'long_name'."]
        ),
        RuleTest(
            dataset=invalid_dataset_2, expected=["Missing attribute 'standard_name'."]
        ),
        RuleTest(
            dataset=invalid_dataset_3,
            kwargs={"attrs": ["description"]},
            expected=["Missing attribute 'description'."],
        ),
    ],
)
