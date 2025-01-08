import numpy as np

from xrlint.plugins.xcube.rules.data_var_colors import DataVarColors

import xarray as xr

from xrlint.testing import RuleTester, RuleTest


def make_dataset():
    dims = ["time", "y", "x"]
    n = 5
    return xr.Dataset(
        attrs=dict(title="v-data"),
        coords={
            dims[2]: xr.DataArray(
                np.linspace(0, 1, n), dims=dims[2], attrs={"units": "m"}
            ),
            dims[1]: xr.DataArray(
                np.linspace(0, 1, n), dims=dims[1], attrs={"units": "m"}
            ),
            dims[0]: xr.DataArray(
                [2010, 2011, 2012, 2013, 2014],
                dims=dims[0],
                attrs={"units": "years"},
            ),
        },
        data_vars={
            "chl": xr.DataArray(
                np.random.random((n, n, n)),
                dims=dims,
                attrs={
                    "units": "mg/m^-3",
                    "color_bar_name": "plasma",
                    "color_value_min": 0,
                    "color_value_max": 100,
                    "color_norm": "log",
                },
            ),
        },
    )


valid_dataset_1 = make_dataset()

invalid_dataset_1 = make_dataset()
invalid_dataset_1.chl.attrs = {
    "units": "mg/m^-3",
    # Missing:
    # "color_bar_name": "plasma",
    # "color_value_min": 0,
    # "color_value_max": 100,
    # "color_norm": "log",
}
invalid_dataset_2 = make_dataset()
invalid_dataset_2.chl.attrs = {
    "units": "mg/m^-3",
    "color_bar_name": "plasma",
    # Missing:
    # "color_value_min": 0,
    # "color_value_max": 100,
    # "color_norm": "log",
}
invalid_dataset_3 = make_dataset()
invalid_dataset_3.chl.attrs = {
    "units": "mg/m^-3",
    "color_bar_name": "plasma",
    "color_value_min": 0,
    "color_value_max": 100,
    "color_norm": "ln",  # wrong
}

LatLonNamingTest = RuleTester.define_test(
    "data-var-colors",
    DataVarColors,
    valid=[
        RuleTest(dataset=valid_dataset_1),
    ],
    invalid=[
        RuleTest(dataset=invalid_dataset_1),
        RuleTest(dataset=invalid_dataset_2),
        RuleTest(dataset=invalid_dataset_3),
    ],
)
