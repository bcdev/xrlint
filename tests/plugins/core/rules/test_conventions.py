#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

import xarray as xr

from xrlint.plugins.core.rules.conventions import Conventions
from xrlint.testing import RuleTest, RuleTester

valid_dataset_0 = xr.Dataset(attrs=dict(Conventions="CF-1.10"))

invalid_dataset_0 = xr.Dataset()
invalid_dataset_1 = xr.Dataset(attrs=dict(Conventions=1.12))
invalid_dataset_2 = xr.Dataset(attrs=dict(Conventions="CF 1.10"))


ConventionsTest = RuleTester.define_test(
    "conventions",
    Conventions,
    valid=[
        RuleTest(dataset=valid_dataset_0),
        RuleTest(dataset=valid_dataset_0, kwargs={"match": r"CF-.*"}),
    ],
    invalid=[
        RuleTest(
            dataset=invalid_dataset_0,
            expected=["Missing attribute 'Conventions'."],
        ),
        RuleTest(
            dataset=invalid_dataset_1,
            expected=["Invalid attribute 'Conventions': 1.12."],
        ),
        RuleTest(
            dataset=invalid_dataset_2,
            kwargs={"match": r"CF-.*"},
            expected=[
                "Invalid attribute 'Conventions': 'CF 1.10' doesn't match 'CF-.*'."
            ],
        ),
    ],
)
