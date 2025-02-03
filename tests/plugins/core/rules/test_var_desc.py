#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

import xarray as xr

from xrlint.plugins.core.rules.var_desc import VarDesc
from xrlint.testing import RuleTest, RuleTester

pressure_attrs = dict(
    long_name="mean sea level pressure",
    units="hPa",
    standard_name="air_pressure_at_sea_level",
)

time_coord = xr.DataArray(
    [1, 2, 3], dims="time", attrs=dict(units="days since 2025-01-01")
)

valid_dataset_0 = xr.Dataset(
    coords=dict(time=time_coord),
)
valid_dataset_1 = xr.Dataset(
    data_vars=dict(pressure=xr.DataArray([1, 2, 3], dims="time", attrs=pressure_attrs)),
    coords=dict(time=time_coord),
)
valid_dataset_2 = xr.Dataset(
    data_vars=dict(
        chl=xr.DataArray(
            [1, 2, 3], dims="time", attrs=dict(description="It is air pressure")
        )
    ),
    coords=dict(time=time_coord),
)

invalid_dataset_0 = xr.Dataset(
    attrs=dict(),
    data_vars=dict(chl=xr.DataArray([1, 2, 3], dims="time", attrs=dict())),
    coords=dict(time=time_coord),
)

invalid_dataset_1 = xr.Dataset(
    attrs=dict(),
    data_vars=dict(
        chl=xr.DataArray(
            [1, 2, 3],
            dims="time",
            attrs=dict(standard_name="air_pressure_at_sea_level"),
        )
    ),
    coords=dict(time=time_coord),
)
invalid_dataset_2 = xr.Dataset(
    attrs=dict(),
    data_vars=dict(
        chl=xr.DataArray(
            [1, 2, 3], dims="time", attrs=dict(long_name="mean sea level pressure")
        )
    ),
    coords=dict(time=time_coord),
)
invalid_dataset_3 = xr.Dataset(
    attrs=dict(),
    data_vars=dict(chl=xr.DataArray([1, 2, 3], dims="time", attrs=pressure_attrs)),
    coords=dict(time=time_coord),
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
