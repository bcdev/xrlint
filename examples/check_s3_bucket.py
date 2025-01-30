import xrlint.all as xrl

URL = "s3://xcube-test/"

xrlint = xrl.XRLint(no_config_lookup=True)
xrlint.init_config("recommended")
results = xrlint.verify_files([URL])
print(xrlint.format_results(results))
