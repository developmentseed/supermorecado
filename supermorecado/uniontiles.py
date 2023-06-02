"""Supermercado.uniontiles but for other TMS.

This submodule is adapted from mapbox/supermercado project:

The MIT License (MIT)

Copyright (c) 2015 Mapbox

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

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


@attr.s
class unionTiles:
    """Uniontiles."""

    tms: morecantile.TileMatrixSet = attr.ib(default=WEB_MERCATOR_TMS)

    def union(self, tiles: npt.NDArray) -> List[Dict]:
        """Union of tiles."""
        xmin, xmax, ymin, ymax = sutils.get_range(tiles)

        zoom = sutils.get_zoom(tiles)

        burn = sutils.burnXYZs(tiles, xmin, xmax, ymin, ymax, 0)

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
                "properties": {},
                "type": "Feature",
            }
            for feature, shapes in features.shapes(
                numpy.asarray(
                    numpy.flipud(numpy.rot90(burn)).astype(numpy.uint8),
                    order="C",
                ),
                transform=afftrans,
            )
            if shapes == 1
        ]
