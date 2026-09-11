#  Copyright © 2025-2026 Brockmann Consult GmbH and contributors.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

import xarray as xr

from xrlint.plugins.core.rules.content_desc import ContentDesc
from xrlint.testing import RuleTest, RuleTester

global_attrs = {
    "title": "OC-Climatology",
    "history": "2025-01-26: created",
}

common_attrs = {
    "institution": "ESA",
    "source": "a.nc; b.nc",
    "references": "!",
    "comment": "?",
}

all_attrs = global_attrs | common_attrs

time_coord = xr.DataArray(
    [1, 2, 3], dims="time", attrs={"units": "days since 2025-01-01"}
)

valid_dataset_0 = xr.Dataset(
    attrs=all_attrs,
    data_vars={"chl": xr.DataArray([1, 2, 3], dims="time", attrs={})},
    coords={"time": time_coord},
)
valid_dataset_1 = xr.Dataset(
    attrs=global_attrs,
    data_vars={"chl": xr.DataArray([1, 2, 3], dims="time", attrs=common_attrs)},
    coords={"time": time_coord},
)
valid_dataset_1a = xr.Dataset(
    attrs=global_attrs,
    data_vars={
        "chl": xr.DataArray([1, 2, 3], dims="time", attrs=common_attrs),
        "crs": xr.DataArray(0, attrs={"grid_mapping_name": "..."}),
    },
    coords={"time": time_coord},
)
valid_dataset_1b = xr.Dataset(
    attrs=global_attrs,
    data_vars={
        "chl": xr.DataArray([1, 2, 3], dims="time", attrs=common_attrs),
        "chl_unc": xr.DataArray(0, attrs={"units": "..."}),
    },
    coords={"time": time_coord},
)
valid_dataset_2 = xr.Dataset(
    attrs=global_attrs,
    data_vars={"chl": xr.DataArray([1, 2, 3], dims="time", attrs={})},
    coords={"time": time_coord},
)
valid_dataset_3 = xr.Dataset(
    attrs=global_attrs,
    data_vars={
        "chl": xr.DataArray([1, 2, 3], dims="time", attrs={"description": "Bla!"})
    },
    coords={"time": time_coord},
)

invalid_dataset_0 = xr.Dataset()
invalid_dataset_1 = xr.Dataset(
    attrs={},
    data_vars={"chl": xr.DataArray([1, 2, 3], dims="time", attrs={})},
    coords={"time": time_coord},
)
invalid_dataset_2 = xr.Dataset(
    attrs=global_attrs,
    data_vars={"chl": xr.DataArray([1, 2, 3], dims="time", attrs={})},
    coords={"time": time_coord},
)

ContentDescTest = RuleTester.define_test(
    "content-desc",
    ContentDesc,
    valid=[
        RuleTest(dataset=valid_dataset_0, name="0"),
        RuleTest(dataset=valid_dataset_1, name="1"),
        RuleTest(dataset=valid_dataset_1a, name="1a"),
        RuleTest(
            dataset=valid_dataset_1b, name="1b", kwargs={"ignored_vars": ["chl_unc"]}
        ),
        RuleTest(dataset=valid_dataset_2, name="2", kwargs={"commons": []}),
        RuleTest(
            dataset=valid_dataset_2, name="2", kwargs={"commons": [], "skip_vars": True}
        ),
        RuleTest(
            dataset=valid_dataset_3, name="3", kwargs={"commons": ["description"]}
        ),
    ],
    invalid=[
        RuleTest(dataset=invalid_dataset_0, expected=2),
        RuleTest(dataset=invalid_dataset_1, expected=6),
        RuleTest(dataset=invalid_dataset_2, kwargs={"skip_vars": True}, expected=4),
    ],
)
