#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

import numpy as np
import xarray as xr

from xrlint.plugins.core.rules.var_flags import VarFlags
from xrlint.testing import RuleTest, RuleTester

valid_dataset_0 = xr.Dataset()
valid_dataset_1 = xr.Dataset(
    attrs=dict(title="sensor-data"),
    data_vars={
        "sensor_status_qc": xr.DataArray(
            [1, 3, 5, 2, 0, 5],
            dims="x",
            attrs=dict(
                long_name="Sensor Status",
                standard_name="status_flag",
                _FillValue=0,
                valid_range=[1, 15],
                flag_masks=[1, 2, 12, 12, 12],
                flag_values=[1, 2, 4, 8, 12],
                flag_meanings=(
                    "low_battery"
                    " hardware_fault"
                    " offline_mode"
                    " calibration_mode"
                    " maintenance_mode"
                ),
            ),
        )
    },
)

# Valid, because and flag_values and flag_meanings are sufficient
valid_dataset_2 = valid_dataset_1.copy()
del valid_dataset_2.sensor_status_qc.attrs["flag_masks"]

# Valid, because and flag_masks and flag_meanings are sufficient
valid_dataset_3 = valid_dataset_1.copy()
del valid_dataset_3.sensor_status_qc.attrs["flag_values"]

# Invalid, because flag_meanings are needed
invalid_dataset_0 = valid_dataset_1.copy()
del invalid_dataset_0.sensor_status_qc.attrs["flag_meanings"]

# Invalid, because flag_values are invalid
invalid_dataset_1 = valid_dataset_1.copy()
invalid_dataset_1.sensor_status_qc.attrs["flag_values"] = "1, 2, 4, 8, 12"

# Invalid, because flag_masks are invalid
invalid_dataset_2 = valid_dataset_1.copy()
invalid_dataset_2.sensor_status_qc.attrs["flag_masks"] = "1, 2, 12, 12, 12"

# Invalid, because flag_values and flag_masks must have same length
invalid_dataset_3 = valid_dataset_1.copy()
invalid_dataset_3.sensor_status_qc.attrs["flag_masks"] = [1, 2, 12]

# Invalid, because missing flag_values and flag_masks
invalid_dataset_4 = valid_dataset_1.copy()
del invalid_dataset_4.sensor_status_qc.attrs["flag_values"]
del invalid_dataset_4.sensor_status_qc.attrs["flag_masks"]

# Invalid, because flag_meanings type is not ok
invalid_dataset_5 = valid_dataset_1.copy()
invalid_dataset_5.sensor_status_qc.attrs["flag_meanings"] = [1, 2, 12, 12, 12]

# Invalid, because flag_meanings length is not ok
invalid_dataset_6 = valid_dataset_1.copy()
invalid_dataset_6.sensor_status_qc.attrs["flag_meanings"] = "a b c"

# Invalid, because flag variable is not int
invalid_dataset_7 = valid_dataset_1.copy()
invalid_dataset_7["sensor_status_qc"] = valid_dataset_1.sensor_status_qc.astype(
    np.float64
)

VarFlagsTest = RuleTester.define_test(
    "var-flags",
    VarFlags,
    valid=[
        RuleTest(dataset=valid_dataset_0),
        RuleTest(dataset=valid_dataset_1),
        RuleTest(dataset=valid_dataset_2),
        RuleTest(dataset=valid_dataset_3),
    ],
    invalid=[
        RuleTest(dataset=invalid_dataset_0, expected=2),
        RuleTest(dataset=invalid_dataset_1, expected=1),
        RuleTest(dataset=invalid_dataset_2, expected=1),
        RuleTest(dataset=invalid_dataset_3, expected=1),
        RuleTest(dataset=invalid_dataset_4, expected=1),
        RuleTest(dataset=invalid_dataset_5, expected=1),
        RuleTest(dataset=invalid_dataset_6, expected=1),
        RuleTest(dataset=invalid_dataset_7, expected=1),
    ],
)
