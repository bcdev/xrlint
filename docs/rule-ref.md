# Rule Reference

## Core Rules

### :material-bug: `coords-for-dims`

Dimensions of data variables should have corresponding coordinates.

Contained in:  `all`-:material-lightning-bolt: `recommended`-:material-lightning-bolt:

### :material-lightbulb: `dataset-title-attr`

Datasets should be given a non-empty title.

Contained in:  `all`-:material-lightning-bolt: `recommended`-:material-alert:

### :material-bug: `grid-mappings`

Grid mappings, if any, shall have valid grid mapping coordinate variables.

Contained in:  `all`-:material-lightning-bolt: `recommended`-:material-lightning-bolt:

### :material-lightbulb: `no-empty-attrs`

Every dataset element should have metadata that describes it.

Contained in:  `all`-:material-lightning-bolt: `recommended`-:material-alert:

### :material-lightbulb: `var-units-attr`

Every variable should have a valid 'units' attribute.

Contained in:  `all`-:material-lightning-bolt: `recommended`-:material-alert:

## xcube Rules

### :material-bug: `any-spatial-data-var`

A datacube should have spatial data variables.
[More information.](https://xcube.readthedocs.io/en/latest/cubespec.html#data-model-and-format)

Contained in:  `all`-:material-lightning-bolt: `recommended`-:material-lightning-bolt:

### :material-bug: `cube-dims-order`

Order of dimensions in spatio-temporal datacube variables should be [time, ..., y, x].
[More information.](https://xcube.readthedocs.io/en/latest/cubespec.html#data-model-and-format)

Contained in:  `all`-:material-lightning-bolt: `recommended`-:material-lightning-bolt:

### :material-lightbulb: `data-var-colors`

Spatial data variables should encode xcube color mappings in their metadata.
[More information.](https://xcube.readthedocs.io/en/latest/cubespec.html#encoding-of-colors)

Contained in:  `all`-:material-lightning-bolt: `recommended`-:material-alert:

### :material-lightbulb: `grid-mapping-naming`

Grid mapping variables should be called 'spatial_ref' or 'crs' for compatibility with rioxarray and other packages.
[More information.](https://xcube.readthedocs.io/en/latest/cubespec.html#spatial-reference)

Contained in:  `all`-:material-lightning-bolt: `recommended`-:material-alert:

### :material-bug: `increasing-time`

Time coordinate labels should be monotonically increasing.
[More information.](https://xcube.readthedocs.io/en/latest/cubespec.html#temporal-reference)

Contained in:  `all`-:material-lightning-bolt: `recommended`-:material-lightning-bolt:

### :material-bug: `lat-lon-naming`

Latitude and longitude coordinates and dimensions should be called 'lat' and 'lon'.
[More information.](https://xcube.readthedocs.io/en/latest/cubespec.html#spatial-reference)

Contained in:  `all`-:material-lightning-bolt: `recommended`-:material-lightning-bolt:

### :material-bug: `single-grid-mapping`

A single grid mapping shall be used for all spatial data variables of a datacube.
[More information.](https://xcube.readthedocs.io/en/latest/cubespec.html#spatial-reference)

Contained in:  `all`-:material-lightning-bolt: `recommended`-:material-lightning-bolt:

