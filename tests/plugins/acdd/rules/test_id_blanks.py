import xarray as xr
from xrlint.testing import RuleTest, RuleTester

from xrlint.plugins.acdd.rules.no_id_blanks import NoBlanksInID

valid_dataset_0 = xr.Dataset(attrs={"id": "testing_dataset"})

invalid_dataset_0 = xr.Dataset()
invalid_dataset_1 = xr.Dataset(attrs={"id": "testing dataset"})


IdBlanksTest = RuleTester.define_test(
    "1.3-no-blanks-in-id",
    NoBlanksInID,
    valid=[RuleTest(dataset=valid_dataset_0)],
    invalid=[
        RuleTest(
            dataset=invalid_dataset_0,
            expected=["Missing attribute 'id'"],
        ),
        RuleTest(
            dataset=invalid_dataset_1,
            expected=["There should not be blanks in the id field"],
        ),
    ],
)
