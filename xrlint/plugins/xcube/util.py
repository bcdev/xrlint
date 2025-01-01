import xarray as xr

from .constants import LAT_NAME, LON_NAME, X_NAME, Y_NAME


def is_spatial_var(var: xr.DataArray) -> bool:
    """Return 'True' if `var` looks like a spatial variable."""
    dims = var.dims
    return (X_NAME in dims and Y_NAME in dims) or (
        LON_NAME in dims and LAT_NAME in dims
    )
