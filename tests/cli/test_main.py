from contextlib import contextmanager
from unittest import TestCase
from click.testing import CliRunner


from xrlint.cli.main import main
from xrlint.version import VERSION


class CliMainTest(TestCase):
    def test_usage_with_defaults(self):
        import xarray as xr

        with new_temp_dir() as _temp_dir:
            datasets = dict(
                dataset1=xr.Dataset(attrs={"title": "Test 1"}),
                dataset2=xr.Dataset(attrs={"title": "Test 2"}),
            )
            files = ["dataset1.zarr", "dataset1.nc", "dataset2.zarr", "dataset2.nc"]
            for file in files:
                name, ext = file.split(".")
                if ext == "zarr":
                    datasets[name].to_zarr(file)
                else:
                    datasets[name].to_netcdf(file)

            runner = CliRunner()
            result = runner.invoke(main, files)
            self.assertEqual(result.exit_code, 0)
            self.assertIn("".join(f"{f} - ok\n" for f in files), result.output)

    def test_help(self):
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Usage: xrlint [OPTIONS] [FILES]...\n", result.output)

    def test_version(self):
        runner = CliRunner()
        result = runner.invoke(main, ["--version"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn(f"xrlint, version {VERSION}", result.output)


@contextmanager
def new_temp_dir() -> str:
    import os
    import tempfile
    import shutil

    temp_dir = tempfile.mkdtemp(prefix="xrlint-cli-test-")
    last_cwd = os.getcwd()
    os.chdir(temp_dir)
    try:
        yield temp_dir
    finally:
        os.chdir(last_cwd)
        shutil.rmtree(temp_dir)
