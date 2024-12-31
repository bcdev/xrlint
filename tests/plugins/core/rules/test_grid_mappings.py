from xrlint.plugins.core.rules.grid_mappings import GridMappings

import numpy as np
import xarray as xr

from xrlint.testing import RuleTest, RuleTester

valid_dataset_1 = xr.Dataset(attrs=dict(title="Empty"))
valid_dataset_2 = xr.Dataset(
    attrs=dict(title="OC Data"),
    coords={
        "x": xr.DataArray(np.linspace(0, 1, 4), dims="x", attrs={"units": "m"}),
        "y": xr.DataArray(np.linspace(0, 1, 3), dims="y", attrs={"units": "m"}),
        "time": xr.DataArray([2022, 2021], dims="time", attrs={"units": "years"}),
        "crs": xr.DataArray(
            0,
            attrs={
                "grid_mapping_name": "latitude_longitude",
                "semi_major_axis": 6371000.0,
                "inverse_flattening": 0,
            },
        ),
    },
    data_vars={
        "chl": xr.DataArray(
            np.random.random((2, 3, 4)),
            dims=["time", "y", "x"],
            attrs={"units": "mg/m^-3", "grid_mapping": "crs"},
        ),
        "tsm": xr.DataArray(
            np.random.random((2, 3, 4)),
            dims=["time", "y", "x"],
            attrs={"units": "mg/m^-3", "grid_mapping": "crs"},
        ),
    },
)

# TODO
# invalid_dataset_1 = valid_dataset_1.copy()
# invalid_dataset_2 = valid_dataset_2.copy()
# invalid_dataset_3 = valid_dataset_2.copy()
# invalid_dataset_1.attrs = {}
# invalid_dataset_2.x.attrs = {}
# invalid_dataset_3.v.attrs = {}


GridMappingsTest = RuleTester.define_test(
    "grid-mappings",
    GridMappings,
    valid=[
        RuleTest(dataset=valid_dataset_1),
        RuleTest(dataset=valid_dataset_2),
    ],
    invalid=[
        # TODO
        # RuleTest(dataset=invalid_dataset_1),
        # RuleTest(dataset=invalid_dataset_2),
        # RuleTest(dataset=invalid_dataset_3),
    ],
)
