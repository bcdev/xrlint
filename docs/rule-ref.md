# Rule Reference

## Core Rules

### `coords-for-dims`

Dimensions of data variables should have corresponding coordinates.

Contained in:  `all`-:material-lightning-bolt: `recommended`-:material-lightning-bolt:

### `dataset-title-attr`

Datasets should be given a non-empty title.

Contained in:  `all`-:material-lightning-bolt: `recommended`-:material-alert:

### `grid-mappings`

Grid mappings, if any, shall have valid grid mapping coordinate variables.

Contained in:  `all`-:material-lightning-bolt: `recommended`-:material-lightning-bolt:

### `no-empty-attrs`

Every dataset element should have metadata that describes it.

Contained in:  `all`-:material-lightning-bolt: `recommended`-:material-alert:

### `var-units-attr`

Every variable should have a valid 'units' attribute.

Contained in:  `all`-:material-lightning-bolt: `recommended`-:material-alert:

## xcube Rules

### `any-spatial-data-var`

A datacube should have spatial data variables.

Contained in:  `all`-:material-lightning-bolt: `recommended`-:material-lightning-bolt:

### `cube-dims-order`

Order of dimensions in spatio-temporal datacube variables should be [time, ..., y, x].

Contained in:  `all`-:material-lightning-bolt: `recommended`-:material-lightning-bolt:

### `grid-mapping-naming`

Grid mapping variables should be called 'spatial_ref' or 'crs' for compatibility with rioxarray and other packages.

Contained in:  `all`-:material-lightning-bolt: `recommended`-:material-alert:

### `lat-lon-naming`

Latitude and longitude coordinates and dimensions should be called 'lat' and 'lon'.

Contained in:  `all`-:material-lightning-bolt: `recommended`-:material-lightning-bolt:

### `single-grid-mapping`

A single grid mapping shall be used for all spatial data variables of a datacube.

Contained in:  `all`-:material-lightning-bolt: `recommended`-:material-lightning-bolt:

