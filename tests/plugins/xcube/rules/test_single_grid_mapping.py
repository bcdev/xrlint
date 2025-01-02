from xrlint.plugins.xcube.rules.single_grid_mapping import SingleGridMapping

import numpy as np
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


valid_dataset_1 = xr.Dataset(attrs=dict(title="Empty"))
valid_dataset_2 = make_dataset()
valid_dataset_3 = make_dataset().rename({"crs": "spatial_ref"})
valid_dataset_4 = make_dataset().drop_vars("crs")
valid_dataset_5 = (
    make_dataset()
    .rename_dims({"x": "lon", "y": "lat"})
    .rename_vars({"x": "lon", "y": "lat"})
    .drop_vars("crs")
)
del valid_dataset_5.chl.attrs["grid_mapping"]
del valid_dataset_5.tsm.attrs["grid_mapping"]

invalid_dataset_1 = make_dataset().copy(deep=True)
invalid_dataset_1.tsm.attrs["grid_mapping"] = "crs2"
invalid_dataset_2 = make_dataset().copy(deep=True)
del invalid_dataset_2.chl.attrs["grid_mapping"]
del invalid_dataset_2.tsm.attrs["grid_mapping"]

SingleGridMappingTest = RuleTester.define_test(
    "single-grid-mapping",
    SingleGridMapping,
    valid=[
        RuleTest(dataset=valid_dataset_1),
        RuleTest(dataset=valid_dataset_2),
        RuleTest(dataset=valid_dataset_3),
        RuleTest(dataset=valid_dataset_4),
        RuleTest(dataset=valid_dataset_5),
    ],
    invalid=[
        RuleTest(dataset=invalid_dataset_1),
        RuleTest(dataset=invalid_dataset_2),
    ],
)
