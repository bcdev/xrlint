from xrlint.plugins.core.rules.grid_mappings import GridMappings

import numpy as np
import xarray as xr

from xrlint.testing import RuleTest, RuleTester


def make_dataset():
    return xr.Dataset(
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


valid_dataset_1 = xr.Dataset(attrs=dict(title="Empty"))
valid_dataset_2 = make_dataset()

invalid_dataset_1 = make_dataset().drop_vars("crs")
invalid_dataset_2 = make_dataset()
crs_var = invalid_dataset_2.coords["crs"]
del invalid_dataset_2.coords["crs"]
invalid_dataset_2["crs"] = crs_var
invalid_dataset_3 = make_dataset()
crs_var = invalid_dataset_3.coords["crs"]
del invalid_dataset_3.coords["crs"]
invalid_dataset_3 = invalid_dataset_3.assign_coords(crs=crs_var.expand_dims("m"))
invalid_dataset_4 = make_dataset()
del invalid_dataset_4["crs"].attrs["grid_mapping_name"]


GridMappingsTest = RuleTester.define_test(
    "grid-mappings",
    GridMappings,
    valid=[
        RuleTest(dataset=valid_dataset_1),
        RuleTest(dataset=valid_dataset_2),
    ],
    invalid=[
        RuleTest(dataset=invalid_dataset_1),
        RuleTest(dataset=invalid_dataset_2),
        RuleTest(dataset=invalid_dataset_3),
        RuleTest(dataset=invalid_dataset_4),
    ],
)
