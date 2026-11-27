"""Indexed, antialiased coastal and freshwater coverage for individual close-up terrain tiles."""

from itertools import chain
import json
import math
from pathlib import Path

import numpy as np
from rasterio.transform import array_bounds
from rasterio.warp import transform_geom
from shapely import STRtree, clip_by_rect, get_parts
from shapely.geometry import box, shape

from build_hydrography import GEOGRAPHIC, Grid, coverage, make_grid, projected_features, source_paths
from pack_atlas import PENNYS_BAY


def index_polygons(features):
    # Split continental polygons once so each raster request only visits local coast segments.
    step = 500_000
    parts = []
    for feature in features:
        for polygon in get_parts(shape(feature)):
            if polygon.geom_type != 'Polygon':
                continue
            left, bottom, right, top = polygon.bounds
            if max(right - left, top - bottom) <= step:
                parts.append(polygon)
                continue
            for y in range(math.floor(bottom / step), math.ceil(top / step)):
                for x in range(math.floor(left / step), math.ceil(right / step)):
                    piece = clip_by_rect(polygon, x * step, y * step, (x + 1) * step, (y + 1) * step)
                    if not piece.is_empty:
                        parts.append(piece)
    return STRtree(parts)


def render_coverage(index, grid, bounds):
    window = box(*bounds)
    candidates = index.geometries.take(index.query(window, predicate='intersects'))
    if any(polygon.covers(window) for polygon in candidates):
        return np.full(grid.shape, 255, dtype=np.uint8)
    shapes = [clip_by_rect(polygon, *bounds) for polygon in candidates]
    shapes = [polygon for polygon in shapes if not polygon.is_empty]
    if not shapes:
        return np.zeros(grid.shape, dtype=np.uint8)
    return np.asarray(coverage(shapes, grid))


class DetailHydro:
    def __init__(self, metadata, cache):
        grid, clip = make_grid(metadata, metadata['width'])
        self.crs = grid.crs
        paths = source_paths(Path(cache), ('land', 'lakes', 'rivers'))
        coast_patch = json.loads(PENNYS_BAY.read_text(encoding='utf-8'))['geometry']
        coast_patch = transform_geom(GEOGRAPHIC, self.crs, coast_patch)
        self.land = index_polygons(chain(projected_features(paths['land'], clip, self.crs), [coast_patch]))
        lakes = projected_features(paths['lakes'], clip, self.crs)
        # Keep the same ranked centerlines as the national atlas. At 256 m per texel
        # their narrower illustrative widths range from about 300 m to 1 km.
        rivers = projected_features(paths['rivers'], clip, self.crs, river=True, river_scale=0.23)
        self.freshwater = index_polygons(chain(lakes, rivers))

    def coverage(self, dimensions, affine):
        """Return land and inland-water coverage (0–255) at the supplied pixel edges."""
        height, width = dimensions
        grid = Grid(width, height, self.crs, affine)
        bounds = array_bounds(height, width, affine)
        return render_coverage(self.land, grid, bounds), render_coverage(self.freshwater, grid, bounds)
