#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

import xarray as xr

from xrlint.plugins.core.rules.no_empty_chunks import NoEmptyChunks
from xrlint.testing import RuleTest, RuleTester

# valid, because it is not chunked
valid_dataset_0 = xr.Dataset(attrs=dict(title="OC-Climatology"))
valid_dataset_0.encoding["source"] = "test.zarr"
valid_dataset_0["sst"] = xr.DataArray([273, 274, 272], dims="time")
valid_dataset_0["sst"].encoding["_FillValue"] = 0
valid_dataset_0["sst"].encoding["chunks"] = [3]
# valid, because it does not apply
valid_dataset_1 = valid_dataset_0.copy()
del valid_dataset_1.encoding["source"]
# valid, because it does not apply
valid_dataset_2 = valid_dataset_0.copy()
valid_dataset_2.encoding["source"] = "test.nc"

# valid, because it does not apply
invalid_dataset_0 = valid_dataset_0.copy()
invalid_dataset_0["sst"].encoding["chunks"] = [1]

NoEmptyChunksTest = RuleTester.define_test(
    "no-empty-chunks",
    NoEmptyChunks,
    valid=[
        RuleTest(dataset=valid_dataset_0),
        RuleTest(dataset=valid_dataset_1),
        RuleTest(dataset=valid_dataset_2),
    ],
    invalid=[
        RuleTest(dataset=invalid_dataset_0, expected=1),
    ],
)
