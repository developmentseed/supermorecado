"""Supermercado.edge_finder

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

import numpy

from supermorecado import super_utils as sutils


def findedges(tiles: numpy.array):
    """Find edges."""
    xmin, xmax, ymin, ymax = sutils.get_range(tiles)

    zoom = sutils.get_zoom(tiles)

    # make an array of shape (xrange + 3, yrange + 3)
    burn = sutils.burnXYZs(tiles, xmin, xmax, ymin, ymax)

    # Create the indixes for rolling
    idxs = sutils.get_idx()

    # Using the indices to roll + stack the array, find the minimum along the rolled / stacked axis
    xys_edge = (
        numpy.min(
            numpy.dstack(
                [numpy.roll(numpy.roll(burn, i[0], 0), i[1], 1) for i in idxs]
            ),
            axis=2,
        )
        ^ burn
    )

    # Set missed non-tiles to False
    xys_edge[burn is False] = False

    # Recreate the tile xyzs, and add the min vals
    xys_edge = numpy.dstack(numpy.where(xys_edge))[0]
    xys_edge[:, 0] += xmin - 1
    xys_edge[:, 1] += ymin - 1

    # Return the edge array
    return numpy.append(
        xys_edge, numpy.zeros((xys_edge.shape[0], 1), dtype=numpy.uint8) + zoom, axis=1
    )
