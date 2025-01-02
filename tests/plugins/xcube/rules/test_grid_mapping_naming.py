import numpy as np

from xrlint.plugins.xcube.rules.grid_mapping_naming import GridMappingNaming

import xarray as xr

from xrlint.testing import RuleTester, RuleTest


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


valid_dataset_1 = make_dataset()
valid_dataset_2 = valid_dataset_1.rename({"crs": "spatial_ref"})
valid_dataset_3 = valid_dataset_1.drop_vars("crs")

invalid_dataset_1 = valid_dataset_1.rename({"crs": "gm"})


GridMappingNamingTest = RuleTester.define_test(
    "grid-mapping-naming",
    GridMappingNaming,
    valid=[
        RuleTest(dataset=valid_dataset_1),
        RuleTest(dataset=valid_dataset_2),
        RuleTest(dataset=valid_dataset_3),
    ],
    invalid=[
        RuleTest(dataset=invalid_dataset_1),
    ],
)
