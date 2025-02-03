#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

import xrlint.all as xrl

URL = "s3://xcube-test/"

xrlint = xrl.XRLint(no_config_lookup=True)
xrlint.init_config("recommended")
results = xrlint.validate_files([URL])
print(xrlint.format_results(results))
