import numpy as np
import xarray as xr

from xrlint.plugins.core.rules.lat_lon_coords import LatCoords
from xrlint.plugins.core.rules.lat_lon_coords import LonCoords
from xrlint.testing import RuleTest
from xrlint.testing import RuleTester

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


LatCoordsTest = RuleTester.define_test(
    "lat-coord",
    LatCoords,
    valid=[
        RuleTest(dataset=valid_dataset_0),
        RuleTest(dataset=valid_dataset_1),
        RuleTest(dataset=valid_dataset_2),
    ],
    invalid=[],
)

LonCoordsTest = RuleTester.define_test(
    "lon-coord",
    LonCoords,
    valid=[
        RuleTest(dataset=valid_dataset_0),
        RuleTest(dataset=valid_dataset_1),
        RuleTest(dataset=valid_dataset_2),
    ],
    invalid=[],
)
