import xrlint.api as xrl
from xrlint.plugins.core.rules.var_units_attr import VarUnitsAttr
import xarray as xr


valid_dataset_1 = xr.Dataset()
valid_dataset_2 = xr.Dataset(
    attrs=dict(title="v-data"),
    coords={"x": xr.DataArray([0, 0.1, 0.2], dims="x", attrs={"units": "s"})},
    data_vars={"v": xr.DataArray([10, 20, 30], dims="x", attrs={"units": "m/s"})},
)

invalid_dataset_1 = valid_dataset_2.copy()
invalid_dataset_2 = valid_dataset_2.copy()
invalid_dataset_3 = valid_dataset_2.copy()

invalid_dataset_1.x.attrs = {}
invalid_dataset_2.v.attrs = {"units": ""}
invalid_dataset_3.v.attrs = {"units": 1}


VarUnitsAttrTest = xrl.RuleTester.define_test(
    "var-units-attr",
    VarUnitsAttr,
    valid=[
        xrl.RuleTest(dataset=valid_dataset_1),
        xrl.RuleTest(dataset=valid_dataset_2),
    ],
    invalid=[
        xrl.RuleTest(dataset=invalid_dataset_1),
        xrl.RuleTest(dataset=invalid_dataset_2),
        xrl.RuleTest(dataset=invalid_dataset_3),
    ],
)
