import numpy as np
import xarray as xr

from xrlint.plugins.core.rules.time_coords import TimeCoords
from xrlint.testing import RuleTest, RuleTester

valid_dataset_0 = xr.Dataset()
valid_dataset_1 = xr.Dataset(
    coords={
        "time": xr.DataArray(
            np.array([3, 4, 5], dtype=np.dtype("datetime64[s]")),
            dims="time",
            attrs={
                "standard_name": "time",
                "long_name": "time",
            },
        ),
    },
    data_vars={
        "pos": xr.DataArray([10, 20, 30], dims="time", attrs={"units": "seconds"})
    },
)
valid_dataset_1.time.encoding["units"] = "seconds since 2000-01-01 00:00:00 +2:00"
valid_dataset_1.time.encoding["calendar"] = "gregorian"

# OK, because with decode_cf=False meta-info is in attrs still
valid_dataset_2 = valid_dataset_1.copy()
del valid_dataset_2.time.encoding["units"]
del valid_dataset_2.time.encoding["calendar"]
valid_dataset_2.time.attrs["units"] = "seconds since 2000-01-01 UTC"
valid_dataset_2.time.attrs["calendar"] = "gregorian"

# OK, because not identified as time
valid_dataset_3 = valid_dataset_1.copy()
del valid_dataset_3.time.attrs["standard_name"]

# OK, because we only look for standard_name
valid_dataset_4 = valid_dataset_1.rename_vars({"time": "tm"})

# Invalid, because long_name is missing
invalid_dataset_0 = valid_dataset_1.copy()
del invalid_dataset_0.time.attrs["long_name"]

# Invalid, because we require units
invalid_dataset_1 = valid_dataset_1.copy(deep=True)
del invalid_dataset_1.time.encoding["units"]

# Invalid, because we require calendar
invalid_dataset_2 = valid_dataset_1.copy(deep=True)
del invalid_dataset_2.time.encoding["calendar"]

# Invalid, because we require TZ units part
invalid_dataset_3 = valid_dataset_1.copy(deep=True)
invalid_dataset_3.time.encoding["units"] = "seconds since 2000-01-01 00:00:00"

# Invalid, because we require units format wrong
invalid_dataset_4 = valid_dataset_1.copy(deep=True)
invalid_dataset_4.time.encoding["units"] = "2000-01-01 00:00:00 UTC"


TimeCoordsTest = RuleTester.define_test(
    "time-coords",
    TimeCoords,
    valid=[
        RuleTest(dataset=valid_dataset_0),
        RuleTest(dataset=valid_dataset_1),
        RuleTest(dataset=valid_dataset_2),
        RuleTest(dataset=valid_dataset_3),
        RuleTest(dataset=valid_dataset_4),
    ],
    invalid=[
        RuleTest(dataset=invalid_dataset_0),
        RuleTest(dataset=invalid_dataset_1),
        RuleTest(dataset=invalid_dataset_2),
        RuleTest(dataset=invalid_dataset_3),
        RuleTest(dataset=invalid_dataset_4),
    ],
)
