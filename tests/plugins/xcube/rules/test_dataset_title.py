#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

import xarray as xr

from xrlint.plugins.xcube.rules.dataset_title import DatasetTitle
from xrlint.testing import RuleTest, RuleTester

valid_dataset_0 = xr.Dataset(attrs=dict(title="OC-Climatology"))
valid_dataset_1 = xr.Dataset(attrs=dict(title="SST-Climatology"))

invalid_dataset_0 = xr.Dataset()
invalid_dataset_1 = xr.Dataset(attrs=dict(title=""))


DatasetTitleTest = RuleTester.define_test(
    "dataset-title",
    DatasetTitle,
    valid=[
        RuleTest(dataset=valid_dataset_0),
        RuleTest(dataset=valid_dataset_1),
    ],
    invalid=[
        RuleTest(dataset=invalid_dataset_0, expected=1),
        RuleTest(dataset=invalid_dataset_1, expected=1),
    ],
)
