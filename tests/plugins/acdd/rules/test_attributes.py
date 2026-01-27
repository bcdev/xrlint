import xarray as xr
from xrlint.testing import RuleTest, RuleTester

from xrlint.plugins.acdd.rules.attributes import (
    Attributes_1_3_Highly_Recommended,
)

valid_1_3_highly_rec_dataset = xr.Dataset(
    attrs={
        "title": "This is only a test",
        "summary": "This is only a test dataset.",
        "keywords": "test, example, sample",
        "Conventions": "ACDD-1.3",
    },
)
invalid_1_3_highly_rec_dataset = xr.Dataset()


Attributes_1_3_Highly_RecommendedTest = RuleTester.define_test(
    "1.3-attrs-highly-recommended",
    Attributes_1_3_Highly_Recommended,
    valid=[RuleTest(dataset=valid_1_3_highly_rec_dataset)],
    invalid=[
        RuleTest(
            dataset=invalid_1_3_highly_rec_dataset,
            expected=[
                "Missing highly recommended attribute 'title'",
                "Missing highly recommended attribute 'keywords'",
                "Missing highly recommended attribute 'summary'",
                "Missing highly recommended attribute 'Conventions'",
            ],
        ),
    ],
)
