"""Tiles heatmap but for other TMS.

adapted from https://github.com/mapbox/supermercado/pull/53
"""

from typing import Dict, List

import attr
import morecantile
import numpy
import numpy.typing as npt
from affine import Affine
from rasterio import features

from supermorecado import super_utils as sutils

WEB_MERCATOR_TMS = morecantile.tms.get("WebMercatorQuad")


def create_density(
    tiles: npt.NDArray, xmin: int, xmax: int, ymin: int, ymax: int, pad: int = 1
) -> numpy.ndarray:
    """Given an ndarray or tiles and range, create a density raster of tile frequency."""
    burn = numpy.zeros(
        (xmax - xmin + (pad * 2 + 1), ymax - ymin + (pad * 2 + 1)), dtype=numpy.uint32
    )
    tiles, counts = numpy.unique(tiles, return_counts=True, axis=0)
    burn[(tiles[:, 0] - xmin + pad, tiles[:, 1] - ymin + pad)] = counts
    return burn


@attr.s
class densityTiles:
    """heatmap."""

    tms: morecantile.TileMatrixSet = attr.ib(default=WEB_MERCATOR_TMS)

    def heatmap(self, tiles: npt.NDArray) -> List[Dict]:
        """Creates a vector "heatmap" of tile densities"""
        xmin, xmax, ymin, ymax = sutils.get_range(tiles)

        zoom = sutils.get_zoom(tiles)

        burn = create_density(tiles, xmin, xmax, ymin, ymax, 0)
        density = numpy.asarray(
            numpy.flipud(numpy.rot90(burn)).astype(numpy.uint8),
            order="C",
        )

        nw = self.tms.xy(*self.tms.ul(xmin, ymin, zoom))
        se = self.tms.xy(*self.tms.ul(xmax + 1, ymax + 1, zoom))
        afftrans = Affine(
            ((se[0] - nw[0]) / float(xmax - xmin + 1)),
            0.0,
            nw[0],
            0.0,
            -((nw[1] - se[1]) / float(ymax - ymin + 1)),
            nw[1],
        )

        unprojecter = sutils.Unprojecter(self.tms)

        return [
            {
                "geometry": unprojecter.unproject(feature),
                "properties": {"n": count},
                "type": "Feature",
            }
            for feature, count in features.shapes(
                density,
                mask=density > 0,
                transform=afftrans,
            )
        ]
