#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

import numpy as np
import xarray as xr

from xrlint.plugins.core.rules.lat_lon_coordinate import LatCoordinate, LonCoordinate
from xrlint.testing import RuleTest, RuleTester

valid_dataset_0 = xr.Dataset()
valid_dataset_1 = xr.Dataset(
    coords={
        "lat": xr.DataArray(
            np.array([3, 4, 5]),
            dims="lat",
            attrs={
                "units": "degrees_north",
                "standard_name": "latitude",
                "long_name": "latitude",
            },
        ),
        "lon": xr.DataArray(
            np.array([-2, -1, 0, 1]),
            dims="lon",
            attrs={
                "units": "degrees_east",
                "standard_name": "longitude",
                "long_name": "longitude",
            },
        ),
    },
    data_vars={
        "mask": xr.DataArray(
            [[10, 20, 30, 40], [30, 40, 50, 60], [50, 60, 70, 80]], dims=("lat", "lon")
        )
    },
)

# Valid, because the coord names doesn't matter as long their metadata is ok
valid_dataset_2 = valid_dataset_1.rename_vars({"lon": "x", "lat": "y"})

# Valid, because the coord units have aliases
valid_dataset_3 = valid_dataset_1.copy()
valid_dataset_3.lat.attrs["units"] = "degreeN"
valid_dataset_3.lon.attrs["units"] = "degreeE"

# Valid, because the coord units have aliases
valid_dataset_4 = valid_dataset_1.copy()
del valid_dataset_4.lat.attrs["standard_name"]
del valid_dataset_4.lon.attrs["standard_name"]
valid_dataset_4.lat.attrs["axis"] = "Y"
valid_dataset_4.lon.attrs["axis"] = "X"

invalid_lat_dataset_0 = valid_dataset_1.copy()
del invalid_lat_dataset_0.lat.attrs["standard_name"]

invalid_lon_dataset_0 = valid_dataset_1.copy()
del invalid_lon_dataset_0.lon.attrs["units"]

invalid_lat_dataset_1 = valid_dataset_1.copy()
invalid_lat_dataset_1.lat.attrs["units"] = "deg"

invalid_lon_dataset_1 = valid_dataset_1.copy()
invalid_lon_dataset_1.lon.attrs["long_name"] = "poo"

invalid_lat_dataset_2 = valid_dataset_1.copy()
del invalid_lat_dataset_2.lat.attrs["standard_name"]
invalid_lat_dataset_2.lat.attrs["axis"] = "y"  # should be "Y"

invalid_lon_dataset_2 = valid_dataset_1.copy()
del invalid_lon_dataset_2.lon.attrs["standard_name"]
invalid_lon_dataset_2.lon.attrs["axis"] = "x"  # should be "X"

LatCoordsTest = RuleTester.define_test(
    "lat-coordinate",
    LatCoordinate,
    valid=[
        RuleTest(dataset=valid_dataset_0),
        RuleTest(dataset=valid_dataset_1),
        RuleTest(dataset=valid_dataset_2),
        RuleTest(dataset=valid_dataset_3),
        RuleTest(dataset=valid_dataset_4),
        RuleTest(dataset=invalid_lon_dataset_0),
        RuleTest(dataset=invalid_lon_dataset_1),
        RuleTest(dataset=invalid_lon_dataset_2),
    ],
    invalid=[
        RuleTest(dataset=invalid_lat_dataset_0, expected=1),
        RuleTest(dataset=invalid_lat_dataset_1, expected=1),
        RuleTest(dataset=invalid_lat_dataset_2, expected=2),
    ],
)

LonCoordsTest = RuleTester.define_test(
    "lon-coordinate",
    LonCoordinate,
    valid=[
        RuleTest(dataset=valid_dataset_0),
        RuleTest(dataset=valid_dataset_1),
        RuleTest(dataset=valid_dataset_2),
        RuleTest(dataset=valid_dataset_3),
        RuleTest(dataset=valid_dataset_4),
        RuleTest(dataset=invalid_lat_dataset_0),
        RuleTest(dataset=invalid_lat_dataset_1),
        RuleTest(dataset=invalid_lat_dataset_2),
    ],
    invalid=[
        RuleTest(dataset=invalid_lon_dataset_0, expected=1),
        RuleTest(dataset=invalid_lon_dataset_1, expected=1),
        RuleTest(dataset=invalid_lon_dataset_2, expected=2),
    ],
)
