#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

import numpy as np
import xarray as xr

from xrlint.plugins.core.rules.time_coordinate import TimeCoordinate
from xrlint.testing import RuleTest, RuleTester

valid_dataset_0 = xr.Dataset()
valid_dataset_1 = xr.Dataset(
    coords={
        "time": xr.DataArray(
            np.array([3, 4, 5], dtype=np.dtype("datetime64[s]")),
            dims="time",
            attrs={
                "standard_name": "time",
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
valid_dataset_2.time.attrs["units"] = "seconds since 2000-1-1 +2:00"
valid_dataset_2.time.attrs["calendar"] = "gregorian"

# OK, because not identified as time
valid_dataset_3 = valid_dataset_1.copy()
del valid_dataset_3.time.encoding["units"]
del valid_dataset_3.time.attrs["standard_name"]

# OK, because we only look for time units
valid_dataset_4 = valid_dataset_1.rename_vars({"time": "tm"})
del valid_dataset_4.tm.attrs["standard_name"]

# OK, because not recognized as time coord
valid_dataset_5 = valid_dataset_1.copy()
valid_dataset_5.time.encoding["units"] = 1
del valid_dataset_5.time.attrs["standard_name"]

# Invalid, because units is invalid but standard_name given
invalid_dataset_0 = valid_dataset_1.copy()
invalid_dataset_0.time.encoding["units"] = 1

# Invalid, because we require units but standard_name given
invalid_dataset_1 = valid_dataset_1.copy(deep=True)
del invalid_dataset_1.time.encoding["units"]

# Invalid, because we no time units although standard_name given
invalid_dataset_2 = valid_dataset_1.copy(deep=True)
invalid_dataset_2.time.encoding["units"] = "years from 2000-1-1 +0:0"

# Invalid, because we require calendar
invalid_dataset_3 = valid_dataset_1.copy(deep=True)
del invalid_dataset_3.time.encoding["calendar"]

# Invalid, because we use invalid UOT
invalid_dataset_4 = valid_dataset_1.copy(deep=True)
invalid_dataset_4.time.encoding["units"] = "millis since 2000-1-1 +0:0"

# Invalid, because we use ambiguous UOT
invalid_dataset_5 = valid_dataset_1.copy(deep=True)
invalid_dataset_5.time.encoding["units"] = "years since 2000-1-1 +0:0"

# Invalid, because we require timezone
invalid_dataset_6 = valid_dataset_1.copy(deep=True)
invalid_dataset_6.time.encoding["units"] = "seconds since 2000-01-01 00:00:00"

# Invalid, because we require timezone
invalid_dataset_7 = valid_dataset_1.copy(deep=True)
invalid_dataset_7.time.encoding["units"] = "seconds since 2000-01-01"

# Invalid, because we have 6 units parts
invalid_dataset_8 = valid_dataset_1.copy(deep=True)
invalid_dataset_8.time.encoding["units"] = "days since 2000-01-01 12:00:00 +0:00 utc"

# Invalid, because we date part is invalid
invalid_dataset_9 = valid_dataset_1.copy(deep=True)
invalid_dataset_9.time.encoding["units"] = "days since 00-01-01 12:00:00 +0:00"

# Invalid, because we time part is invalid
invalid_dataset_10 = valid_dataset_1.copy(deep=True)
invalid_dataset_10.time.encoding["units"] = "days since 2000-01-01 12:00 +0:00"

# Invalid, because we tz part is invalid
invalid_dataset_11 = valid_dataset_1.copy(deep=True)
invalid_dataset_11.time.encoding["units"] = "days since 2000-01-01 12:00:00 utc"

TimeCoordinateTest = RuleTester.define_test(
    "time-coordinate",
    TimeCoordinate,
    valid=[
        RuleTest(dataset=valid_dataset_0),
        RuleTest(dataset=valid_dataset_1),
        RuleTest(dataset=valid_dataset_2),
        RuleTest(dataset=valid_dataset_3),
        RuleTest(dataset=valid_dataset_4),
        RuleTest(dataset=valid_dataset_5),
    ],
    invalid=[
        RuleTest(dataset=invalid_dataset_0, expected=1),
        RuleTest(dataset=invalid_dataset_1, expected=1),
        RuleTest(dataset=invalid_dataset_2, expected=1),
        RuleTest(dataset=invalid_dataset_3, expected=1),
        RuleTest(dataset=invalid_dataset_4, expected=1),
        RuleTest(dataset=invalid_dataset_5, expected=1),
        RuleTest(dataset=invalid_dataset_6, expected=1),
        RuleTest(dataset=invalid_dataset_7, expected=1),
        RuleTest(dataset=invalid_dataset_8, expected=1),
        RuleTest(dataset=invalid_dataset_9, expected=1),
        RuleTest(dataset=invalid_dataset_10, expected=1),
        RuleTest(dataset=invalid_dataset_11, expected=1),
    ],
)
