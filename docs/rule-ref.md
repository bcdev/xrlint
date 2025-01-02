# Rule Reference

## Core Rules

### `coords-for-dims`

Dimensions of data variables should have corresponding coordinates.

### `dataset-title-attr`

Datasets should be given a non-empty title.

### `grid-mappings`

Grid mappings, if any, shall have valid grid mapping coordinate variables.

### `no-empty-attrs`

Every dataset element should have metadata that describes it.

### `var-units-attr`

Every variable should have a valid 'units' attribute.

## xcube Rules

### `any-spatial-data-var`

A datacube should have spatial data variables.

### `cube-dims-order`

Order of dimensions in spatio-temporal datacube variables should be [time, ..., y, x].

### `grid-mapping-naming`

Grid mapping variables should be called 'spatial_ref' or 'crs' for compatibility with rioxarray and other packages.

### `lat-lon-naming`

Latitude and longitude coordinates and dimensions should be called 'lat' and 'lon'.

### `single-grid-mapping`

A single grid mapping shall be used for all spatial data variables of a datacube.

