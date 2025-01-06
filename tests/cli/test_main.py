import os
import tempfile
import shutil
from unittest import TestCase

from click.testing import CliRunner
import xarray as xr

from xrlint.cli.main import main
from xrlint.cli.constants import DEFAULT_CONFIG_FILE_YAML
from xrlint.version import version
from .helpers import text_file


# noinspection PyTypeChecker
class CliMainTest(TestCase):
    files = ["dataset1.zarr", "dataset1.nc", "dataset2.zarr", "dataset2.nc"]

    ok_config_yaml = "- rules:\n    dataset-title-attr: error\n"
    fail_config_yaml = "- rules:\n    no-empty-attrs: error\n"

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

    def test_no_files(self):
        runner = CliRunner()
        result = runner.invoke(main)
        self.assertIn("No dataset files provided.", result.output)
        self.assertEqual(1, result.exit_code)

    def test_files_no_rules(self):
        runner = CliRunner()
        result = runner.invoke(main, self.files)
        self.assertIn("Warning: no configuration file found.", result.output)
        self.assertIn("No rules configured or applicable.", result.output)
        self.assertEqual(1, result.exit_code)

    def test_files_one_rule(self):
        with text_file(DEFAULT_CONFIG_FILE_YAML, self.ok_config_yaml):
            runner = CliRunner()
            result = runner.invoke(main, ["--no-color"] + self.files)
            self.assertEqual(
                "\n"
                "dataset1.zarr - ok\n\n"
                "dataset1.nc - ok\n\n"
                "dataset2.zarr - ok\n\n"
                "dataset2.nc - ok\n\n"
                "no problems\n\n",
                result.output,
            )
            self.assertEqual(0, result.exit_code)

        with text_file(DEFAULT_CONFIG_FILE_YAML, self.fail_config_yaml):
            runner = CliRunner()
            result = runner.invoke(main, self.files)
            self.assertIn("Missing metadata, attributes are empty.", result.output)
            self.assertIn("no-empty-attrs", result.output)
            self.assertEqual(1, result.exit_code)

    def test_dir_one_rule(self):
        with text_file(DEFAULT_CONFIG_FILE_YAML, self.ok_config_yaml):
            runner = CliRunner()
            result = runner.invoke(main, ["--no-color", "."])
            prefix = self.temp_dir.replace("\\", "/")
            self.assertIn(f"{prefix}/dataset1.zarr - ok\n\n", result.output)
            self.assertIn(f"{prefix}/dataset1.nc - ok\n\n", result.output)
            self.assertIn(f"{prefix}/dataset2.zarr - ok\n\n", result.output)
            self.assertIn(f"{prefix}/dataset2.nc - ok\n\n", result.output)
            self.assertIn("no problems\n\n", result.output)
            self.assertEqual(0, result.exit_code)

        with text_file(DEFAULT_CONFIG_FILE_YAML, self.fail_config_yaml):
            runner = CliRunner()
            result = runner.invoke(main, self.files)
            self.assertIn("Missing metadata, attributes are empty.", result.output)
            self.assertIn("no-empty-attrs", result.output)
            self.assertEqual(1, result.exit_code)

    def test_color_no_color(self):
        with text_file(DEFAULT_CONFIG_FILE_YAML, self.ok_config_yaml):
            runner = CliRunner()
            result = runner.invoke(main, ["--no-color"] + self.files)
            self.assertEqual(
                "\n"
                "dataset1.zarr - ok\n\n"
                "dataset1.nc - ok\n\n"
                "dataset2.zarr - ok\n\n"
                "dataset2.nc - ok\n\n"
                "no problems\n\n",
                result.output,
            )
            self.assertEqual(0, result.exit_code)

        with text_file(DEFAULT_CONFIG_FILE_YAML, self.ok_config_yaml):
            runner = CliRunner()
            result = runner.invoke(main, ["--color"] + self.files)
            self.assertEqual(
                "\n\x1b[4mdataset1.zarr\x1b[0m - ok\n\n"
                "\x1b[4mdataset1.nc\x1b[0m - ok\n\n"
                "\x1b[4mdataset2.zarr\x1b[0m - ok\n\n"
                "\x1b[4mdataset2.nc\x1b[0m - ok\n\n"
                "no problems\n\n",
                result.output,
            )
            self.assertEqual(0, result.exit_code)

    def test_files_with_rule_option(self):
        runner = CliRunner()
        result = runner.invoke(
            main,
            [
                "--rule",
                "no-empty-attrs: error",
            ]
            + self.files,
        )
        self.assertIn("Missing metadata, attributes are empty.", result.output)
        self.assertIn("no-empty-attrs", result.output)
        self.assertEqual(1, result.exit_code)

    def test_files_with_plugin_and_rule_options(self):
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
        self.assertEqual(1, result.exit_code)

    def test_files_with_output_file(self):
        with text_file(DEFAULT_CONFIG_FILE_YAML, self.ok_config_yaml):
            runner = CliRunner()
            result = runner.invoke(main, ["-o", "memory://report.txt"] + self.files)
            self.assertEqual("", result.output)
            self.assertEqual(0, result.exit_code)

    def test_files_but_config_file_missing(self):
        runner = CliRunner()
        result = runner.invoke(main, ["-c", "pippo.py"] + self.files)
        self.assertIn("Error: file not found: pippo.py", result.output)
        self.assertEqual(1, result.exit_code)

    def test_files_with_format_option(self):
        with text_file(DEFAULT_CONFIG_FILE_YAML, self.ok_config_yaml):
            runner = CliRunner()
            result = runner.invoke(main, ["-f", "json"] + self.files)
            self.assertIn('"results": [\n', result.output)
            self.assertEqual(0, result.exit_code)

    def test_files_with_invalid_format_option(self):
        runner = CliRunner()
        result = runner.invoke(main, ["-f", "foo"] + self.files)
        self.assertIn(
            "Error: unknown format 'foo'. The available formats are '", result.output
        )
        self.assertEqual(1, result.exit_code)

    def test_init(self):
        config_file = DEFAULT_CONFIG_FILE_YAML
        exists = os.path.exists(config_file)
        self.assertFalse(exists)
        try:
            runner = CliRunner()
            result = runner.invoke(main, ["--init"])
            self.assertEqual(
                f"Configuration template written to {config_file}\n", result.output
            )
            self.assertEqual(result.exit_code, 0)
            exists = os.path.exists(config_file)
            self.assertTrue(exists)
        finally:
            if exists:
                os.remove(config_file)

    def test_init_exists(self):
        config_file = DEFAULT_CONFIG_FILE_YAML
        exists = os.path.exists(config_file)
        self.assertFalse(exists)
        with text_file(config_file, ""):
            runner = CliRunner()
            result = runner.invoke(main, ["--init"])
            self.assertEqual(
                f"Error: file {config_file} already exists.\n", result.output
            )
            self.assertEqual(result.exit_code, 1)


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
