#  Copyright © 2025-2026 Brockmann Consult GmbH and contributors.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

import xarray as xr

from xrlint.plugins.acdd.rules.metadata_link import MetadataLink
from xrlint.testing import RuleTest, RuleTester

valid_dataset_0 = xr.Dataset(attrs={"metadata_link": "http://example.com/metadata"})
valid_dataset_1 = xr.Dataset(attrs={"metadata_link": "https://example.com/metadata"})
valid_dataset_2 = xr.Dataset()

invalid_dataset_0 = xr.Dataset(attrs={"metadata_link": "example.com/metadata"})

Metadata_LinkTest = RuleTester.define_test(
    "1.3-metadata-link",
    MetadataLink,
    valid=[
        RuleTest(dataset=valid_dataset_0),
        RuleTest(dataset=valid_dataset_1),
        RuleTest(dataset=valid_dataset_2),
    ],
    invalid=[
        RuleTest(
            dataset=invalid_dataset_0,
            expected=[
                "Metadata URL should include http:// or https://: 'example.com/metadata'",
            ],
        ),
    ],
)
