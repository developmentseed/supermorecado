"""Morecantile command line interface"""

import json

import click
import cligj
import morecantile

from supermorecado import burntiles, edge_finder, super_utils, uniontiles


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
    tiles = edge_finder.findedges(inputtiles, parsenames)
    for t in tiles:
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
def union(inputtiles, parsenames, identifier):
    """
    Returns the unioned shape of a stream of [<x>, <y>, <z>] tiles in GeoJSON.
    """
    tms = morecantile.tms.get(identifier)

    try:
        inputtiles = click.open_file(inputtiles).readlines()
    except IOError:
        inputtiles = [inputtiles]

    unioned = uniontiles.unionTiles(tms).union(inputtiles, parsenames)
    for u in unioned:
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
def burn(features, sequence, zoom, identifier):
    """
    Burn a stream of GeoJSONs into a output stream of the tiles they intersect for a given zoom.
    """
    tms = morecantile.tms.get(identifier)

    features = list(super_utils.filter_features(features))

    tiles = burntiles.burnTiles(tms).burn(features, zoom)
    for t in tiles:
        click.echo(t.tolist())
