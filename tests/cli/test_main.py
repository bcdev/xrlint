import os
import tempfile
import shutil
from unittest import TestCase

from click.testing import CliRunner
import xarray as xr

from xrlint.cli.main import main
from xrlint.version import version


# noinspection PyTypeChecker
class CliMainTest(TestCase):
    files = ["dataset1.zarr", "dataset1.nc", "dataset2.zarr", "dataset2.nc"]

    datasets = dict(
        dataset1=xr.Dataset(attrs={"title": "Test 1"}),
        dataset2=xr.Dataset(
            attrs={"title": "Test 2"}, data_vars={"v": xr.DataArray([1, 2, 3])}
        ),
    )

    temp_dir: str
    last_cwd: str

    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.mkdtemp(prefix="xrlint-")
        cls.last_cwd = os.getcwd()
        os.chdir(cls.temp_dir)

        for file in cls.files:
            name, ext = file.split(".")
            if ext == "zarr":
                cls.datasets[name].to_zarr(file)
            else:
                cls.datasets[name].to_netcdf(file)

    @classmethod
    def tearDownClass(cls):
        os.chdir(cls.last_cwd)
        shutil.rmtree(cls.temp_dir)

    def test_files_no_rules(self):
        runner = CliRunner()
        result = runner.invoke(main, self.files)
        self.assertIn("No rules configured or applicable.", result.output)
        self.assertEqual(result.exit_code, 0)

    def test_files_one_rule_by_config_file(self):
        with open("xrlint.config.yaml", "w") as f:
            f.write('- rules:\n    "no-empty-attrs": error\n')
        runner = CliRunner()
        result = runner.invoke(main, self.files)
        self.assertIn("".join(f"\n{f} - ok\n" for f in self.files), result.output)
        self.assertEqual(result.exit_code, 0)

    def test_files_one_rule_by_rule_option(self):
        runner = CliRunner()
        result = runner.invoke(
            main,
            [
                "--rule",
                "no-empty-attrs: error",
            ]
            + self.files,
        )
        self.assertIn("".join(f"\n{f} - ok\n" for f in self.files), result.output)
        self.assertEqual(result.exit_code, 0)

    def test_files_one_rule_by_plugin_and_rule_options(self):
        runner = CliRunner()
        result = runner.invoke(
            main,
            [
                "--plugin",
                "xrlint.plugins.xcube",
                "--rule",
                "xcube/any-spatial-data-var: error",
            ]
            + self.files,
        )
        self.assertIn("No spatial data variables found.", result.output)
        self.assertIn("xcube/any-spatial-data-var", result.output)
        self.assertEqual(result.exit_code, 0)

    def test_output_file(self):
        runner = CliRunner()
        result = runner.invoke(main, ["-o", "memory://report.txt"] + self.files)
        self.assertEqual(result.exit_code, 0)

    def test_config_missing(self):
        runner = CliRunner()
        result = runner.invoke(main, ["-c", "pippo.py"] + self.files)
        self.assertIn("Error: pippo.py: file not found", result.output)
        self.assertEqual(result.exit_code, 1)

    def test_format(self):
        runner = CliRunner()
        result = runner.invoke(main, ["-f", "json"] + self.files)
        self.assertIn('"results": [\n', result.output)
        self.assertEqual(result.exit_code, 0)

    def test_unknown_format(self):
        runner = CliRunner()
        result = runner.invoke(main, ["-f", "foo"] + self.files)
        self.assertIn(
            "Error: unknown format 'foo'. The available formats are '", result.output
        )
        self.assertEqual(result.exit_code, 1)


# noinspection PyTypeChecker
class CliMainMetaTest(TestCase):

    def test_help(self):
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])
        self.assertIn("Usage: xrlint [OPTIONS] [FILES]...\n", result.output)
        self.assertEqual(result.exit_code, 0)

    def test_version(self):
        runner = CliRunner()
        result = runner.invoke(main, ["--version"])
        self.assertIn(f"xrlint, version {version}", result.output)
        self.assertEqual(result.exit_code, 0)
