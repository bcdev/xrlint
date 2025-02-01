# Rule Reference

This page is auto-generated from XRLint's builtin rules (`python -m mkruleref`).
New rules will be added by upcoming XRLint releases.

## Core Rules

### :material-lightbulb: `content-desc`

A dataset should provide information about where the data came from and what has been done to it. This information is mainly for the benefit of human readers. The rule accepts the following configuration parameters:

- `globals`: list of names of required global attributes. Defaults to `['title', 'history']`.
- `commons`: list of names of required variable attributes that can also be defined globally. Defaults to `['institution', 'source', 'references', 'comment']`.
- `no_vars`: do not check variables at all. Defaults to `False`.
- `ignored_vars`: list of ignored variables (regex patterns). Defaults to `['crs', 'spatial_ref']`.

[:material-information-variant:](https://cfconventions.org/cf-conventions/cf-conventions.html#description-of-file-contents)

Contained in:  `all`-:material-lightning-bolt: `recommended`-:material-alert:

### :material-lightbulb: `conventions`

Datasets should identify the applicable conventions using the `Conventions` attribute.
 The rule has an optional configuration parameter `match` which is a regex pattern that the value of the `Conventions` attribute must match, if any. If not provided, the rule just verifies that the attribute exists and whether it is a character string.
[:material-information-variant:](https://cfconventions.org/cf-conventions/cf-conventions.html#identification-of-conventions)

Contained in:  `all`-:material-lightning-bolt: `recommended`-:material-alert:

### :material-bug: `coords-for-dims`

Dimensions of data variables should have corresponding coordinates.

Contained in:  `all`-:material-lightning-bolt: `recommended`-:material-lightning-bolt:

### :material-bug: `grid-mappings`

Grid mappings, if any, shall have valid grid mapping coordinate variables.

Contained in:  `all`-:material-lightning-bolt: `recommended`-:material-lightning-bolt:

### :material-bug: `lat-coordinate`

Latitude coordinate should have standard units and standard names.
[:material-information-variant:](https://cfconventions.org/cf-conventions/cf-conventions.html#latitude-coordinate)

Contained in:  `all`-:material-lightning-bolt: `recommended`-:material-lightning-bolt:

### :material-bug: `lon-coordinate`

Longitude coordinate should have standard units and standard names.
[:material-information-variant:](https://cfconventions.org/cf-conventions/cf-conventions.html#longitude-coordinate)

Contained in:  `all`-:material-lightning-bolt: `recommended`-:material-lightning-bolt:

### :material-lightbulb: `no-empty-attrs`

Every dataset element should have metadata that describes it.

Contained in:  `all`-:material-lightning-bolt: `recommended`-:material-alert:

### :material-lightbulb: `no-empty-chunks`

Empty chunks should not be encoded and written. The rule currently applies to Zarr format only.
[:material-information-variant:](https://docs.xarray.dev/en/stable/generated/xarray.Dataset.to_zarr.html#xarray-dataset-to-zarr)

Contained in:  `all`-:material-lightning-bolt: `recommended`-:material-circle-off-outline:

### :material-bug: `time-coordinate`

Time coordinates should have valid and unambiguous time units encoding.
[:material-information-variant:](https://cfconventions.org/cf-conventions/cf-conventions.html#time-coordinate)

Contained in:  `all`-:material-lightning-bolt: `recommended`-:material-lightning-bolt:

### :material-lightbulb: `var-desc`

Check that each data variable provides an identification and description of the content. The rule can be configured by parameter `attrs` which is a list of names of attributes that provides descriptive information. It defaults to `['standard_name', 'long_name']`.
[:material-information-variant:](https://cfconventions.org/cf-conventions/cf-conventions.html#standard-name)

Contained in:  `all`-:material-lightning-bolt: `recommended`-:material-alert:

### :material-lightbulb: `var-flags`

Validate attributes 'flag_values', 'flag_masks' and 'flag_meanings' that make variables that contain flag values self describing. 
[:material-information-variant:](https://cfconventions.org/cf-conventions/cf-conventions.html#flags)

Contained in:  `all`-:material-lightning-bolt: `recommended`-:material-lightning-bolt:

### :material-lightbulb: `var-units`

Every variable should provide a description of its units.
[:material-information-variant:](https://cfconventions.org/cf-conventions/cf-conventions.html#units)

Contained in:  `all`-:material-lightning-bolt: `recommended`-:material-alert:

## xcube Rules

### :material-bug: `any-spatial-data-var`

A datacube should have spatial data variables.
[:material-information-variant:](https://xcube.readthedocs.io/en/latest/cubespec.html#data-model-and-format)

Contained in:  `all`-:material-lightning-bolt: `recommended`-:material-lightning-bolt:

### :material-bug: `cube-dims-order`

Order of dimensions in spatio-temporal datacube variables should be [time, ..., y, x].
[:material-information-variant:](https://xcube.readthedocs.io/en/latest/cubespec.html#data-model-and-format)

Contained in:  `all`-:material-lightning-bolt: `recommended`-:material-lightning-bolt:

### :material-lightbulb: `data-var-colors`

Spatial data variables should encode xcube color mappings in their metadata.
[:material-information-variant:](https://xcube.readthedocs.io/en/latest/cubespec.html#encoding-of-colors)

Contained in:  `all`-:material-lightning-bolt: `recommended`-:material-alert:

### :material-bug: `dataset-title`

Datasets should be given a non-empty title.
[:material-information-variant:](https://xcube.readthedocs.io/en/latest/cubespec.html#metadata)

Contained in:  `all`-:material-lightning-bolt: `recommended`-:material-lightning-bolt:

### :material-lightbulb: `grid-mapping-naming`

Grid mapping variables should be called 'spatial_ref' or 'crs' for compatibility with rioxarray and other packages.
[:material-information-variant:](https://xcube.readthedocs.io/en/latest/cubespec.html#spatial-reference)

Contained in:  `all`-:material-lightning-bolt: `recommended`-:material-alert:

### :material-bug: `increasing-time`

Time coordinate labels should be monotonically increasing.
[:material-information-variant:](https://xcube.readthedocs.io/en/latest/cubespec.html#temporal-reference)

Contained in:  `all`-:material-lightning-bolt: `recommended`-:material-lightning-bolt:

### :material-bug: `lat-lon-naming`

Latitude and longitude coordinates and dimensions should be called 'lat' and 'lon'.
[:material-information-variant:](https://xcube.readthedocs.io/en/latest/cubespec.html#spatial-reference)

Contained in:  `all`-:material-lightning-bolt: `recommended`-:material-lightning-bolt:

### :material-lightbulb: `ml-dataset-meta`

Multi-level datasets should provide a '.zlevels' meta-info file, and if so, it should be consistent. Without the meta-info file the multi-level dataset cannot be reliably extended by new time slices as the aggregation method used for each variable must be specified.
[:material-information-variant:](https://xcube.readthedocs.io/en/latest/mldatasets.html#the-xcube-levels-format)

Contained in:  `all`-:material-lightning-bolt: `recommended`-:material-lightning-bolt:

### :material-bug: `ml-dataset-time`

The `time` dimension of multi-level datasets should use a chunk size of 1. This allows for faster image tile generation for visualisation.
[:material-information-variant:](https://xcube.readthedocs.io/en/latest/mldatasets.html#definition)

Contained in:  `all`-:material-lightning-bolt: `recommended`-:material-alert:

### :material-bug: `ml-dataset-xy`

Multi-level dataset levels should provide spatial resolutions decreasing by powers of two.
[:material-information-variant:](https://xcube.readthedocs.io/en/latest/mldatasets.html#definition)

Contained in:  `all`-:material-lightning-bolt: `recommended`-:material-lightning-bolt:

### :material-bug: `no-chunked-coords`

Coordinate variables should not be chunked. Can be used to identify performance issues, where chunked coordinates can cause slow opening if datasets due to the many chunk-fetching requests made to (remote) filesystems with low bandwidth. You can use the `limit` parameter to specify an acceptable number  of chunks. Its default is 5.

Contained in:  `all`-:material-lightning-bolt: `recommended`-:material-alert:

### :material-bug: `single-grid-mapping`

A single grid mapping shall be used for all spatial data variables of a datacube.
[:material-information-variant:](https://xcube.readthedocs.io/en/latest/cubespec.html#spatial-reference)

Contained in:  `all`-:material-lightning-bolt: `recommended`-:material-lightning-bolt:

### :material-bug: `time-naming`

Time coordinate and dimension should be called 'time'.
[:material-information-variant:](https://xcube.readthedocs.io/en/latest/cubespec.html#temporal-reference)

Contained in:  `all`-:material-lightning-bolt: `recommended`-:material-lightning-bolt:

