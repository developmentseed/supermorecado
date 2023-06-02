"""Morecantile command line interface"""

import json

import click
import cligj
import morecantile

from supermorecado import burnTiles, findedges
from supermorecado import super_utils as sutils
from supermorecado import unionTiles


@click.group(help="Command line interface for the Supermorecado Python package.")
def cli():
    """Supermorecado CLI."""
    pass


@cli.command(
    short_help="For a stream of [<x>, <y>, <z>] tiles, return only those tiles that are on the edge."
)
@click.argument("inputtiles", default="-", required=False)
@click.option("--parsenames", is_flag=True)
def edges(inputtiles, parsenames):
    """
    For a stream of [<x>, <y>, <z>] tiles, return only those tiles that are on the edge.
    """
    try:
        inputtiles = click.open_file(inputtiles).readlines()
    except IOError:
        inputtiles = [inputtiles]

    # parse the input stream into an array
    tiles = sutils.tile_parser(inputtiles, parsenames)
    for t in findedges(tiles):
        click.echo(t.tolist())


@cli.command(
    short_help="Returns the unioned shape of a stream of [<x>, <y>, <z>] tiles in GeoJSON."
)
@click.argument("inputtiles", default="-", required=False)
@click.option("--parsenames", is_flag=True)
@click.option(
    "--identifier",
    type=click.Choice(morecantile.tms.list()),
    default="WebMercatorQuad",
    help="TileMatrixSet identifier.",
)
@click.option(
    "--tms",
    help="Path to TileMatrixSet JSON file.",
    type=click.Path(),
)
def union(inputtiles, parsenames, identifier, tms):
    """
    Returns the unioned shape of a stream of [<x>, <y>, <z>] tiles in GeoJSON.
    """
    try:
        inputtiles = click.open_file(inputtiles).readlines()
    except IOError:
        inputtiles = [inputtiles]

    tiles = sutils.tile_parser(inputtiles, parsenames)

    tilematrixset = morecantile.tms.get(identifier)
    if tms:
        with open(tms, "r") as f:
            tilematrixset = morecantile.TileMatrixSet(**json.load(f))

    uniontiles = unionTiles(tms=tilematrixset)
    for u in uniontiles.union(tiles):
        click.echo(json.dumps(u))


@cli.command(
    short_help="Burn a stream of GeoJSONs into a output stream of the tiles they intersect for a given zoom."
)
@cligj.features_in_arg
@cligj.sequence_opt
@click.argument("zoom", type=int)
@click.option(
    "--identifier",
    type=click.Choice(morecantile.tms.list()),
    default="WebMercatorQuad",
    help="TileMatrixSet identifier.",
)
@click.option(
    "--tms",
    help="Path to TileMatrixSet JSON file.",
    type=click.Path(),
)
def burn(features, sequence, zoom, identifier, tms):
    """
    Burn a stream of GeoJSONs into a output stream of the tiles they intersect for a given zoom.
    """
    features = list(sutils.filter_features(features))

    tilematrixset = morecantile.tms.get(identifier)
    if tms:
        with open(tms, "r") as f:
            tilematrixset = morecantile.TileMatrixSet(**json.load(f))

    burntiles = burnTiles(tms=tilematrixset)
    for t in burntiles.burn(features, zoom):
        click.echo(t.tolist())
