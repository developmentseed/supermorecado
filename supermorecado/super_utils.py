"""Supermercado.super_utils but for other TMS.

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
import json
import re
from typing import Any, Dict, Generator, Sequence, Tuple

import attr
import morecantile
import numpy
import numpy.typing as npt


def parseString(tilestring, matcher):
    """Parse Tile."""
    tile = [int(r) for r in matcher.match(tilestring).group().split("-")]
    tile.append(tile.pop(0))
    return tile


def get_range(xyz: npt.NDArray) -> Tuple[int, int, int, int]:
    """Get tiles extrema."""
    return xyz[:, 0].min(), xyz[:, 0].max(), xyz[:, 1].min(), xyz[:, 1].max()


def burnXYZs(
    tiles: npt.NDArray, xmin: float, xmax: float, ymin: float, ymax: float, pad: int = 1
):
    """Burn XYZ tiles."""
    # make an array of shape (xrange + 3, yrange + 3)
    burn = numpy.zeros(
        (xmax - xmin + (pad * 2 + 1), ymax - ymin + (pad * 2 + 1)), dtype=bool
    )

    # using the tile xys as indicides, burn in True where a tile exists
    burn[(tiles[:, 0] - xmin + pad, tiles[:, 1] - ymin + pad)] = True

    return burn


def tile_parser(tiles: npt.ArrayLike, parsenames: bool = False) -> numpy.ndarray:
    """Parse Tile."""
    if parsenames:
        tMatch = re.compile(r"[\d]+-[\d]+-[\d]+")
        tiles = numpy.array([parseString(t, tMatch) for t in tiles])
    else:
        tiles = numpy.array([json.loads(t) for t in tiles])

    return tiles


def get_idx() -> numpy.ndarray:
    """Get numpy identity matrix."""
    tt = numpy.zeros((3, 3), dtype=bool)
    tt[1, 1] = True
    return numpy.dstack(numpy.where(~tt))[0] - 1


def get_zoom(tiles: npt.NDArray) -> int:
    """Get Zoom."""
    t, d = tiles.shape
    if t < 1 or d != 3:
        raise ValueError("Tiles must be of shape n, 3")

    if tiles[:, 2].min() != tiles[:, 2].max():
        raise ValueError("All tile zooms must be the same")

    return tiles[0, 2]


def filter_features(  # noqa: C901
    features: Sequence[Dict[Any, Any]]
) -> Generator[Dict, None, None]:
    """Filter feature."""
    for f in features:
        if "geometry" in f and "type" in f["geometry"]:
            if f["geometry"]["type"] == "Polygon":
                yield f

            elif f["geometry"]["type"] == "Point":
                yield f

            elif f["geometry"]["type"] == "LineString":
                yield f

            elif f["geometry"]["type"] == "MultiPolygon":
                for part in f["geometry"]["coordinates"]:
                    yield {
                        "type": "Feature",
                        "geometry": {"type": "Polygon", "coordinates": part},
                    }

            elif f["geometry"]["type"] == "MultiPoint":
                for part in f["geometry"]["coordinates"]:
                    yield {
                        "type": "Feature",
                        "geometry": {"type": "Point", "coordinates": part},
                    }

            elif f["geometry"]["type"] == "MultiLineString":
                for part in f["geometry"]["coordinates"]:
                    yield {
                        "type": "Feature",
                        "geometry": {"type": "LineString", "coordinates": part},
                    }


@attr.s
class Unprojecter:
    """Convert feature from TMS crs to the TMS's geographic CRS."""

    tms: morecantile.TileMatrixSet = attr.ib()

    def xy_to_lng_lat(
        self, coordinates: Sequence[Tuple[float, float]]
    ) -> numpy.ndarray:
        """Convert coordinates."""
        for c in coordinates:
            tc = numpy.array(c)
            yield numpy.dstack(
                [*self.tms._to_geographic.transform(tc[:, 0], tc[:, 1])]
            )[0].tolist()

    def unproject(self, feature: Dict[Any, Any]) -> Dict[Any, Any]:
        """Apply reprojection."""
        feature["coordinates"] = list(self.xy_to_lng_lat(feature["coordinates"]))
        return feature
