# Supermorecado


<p align="center">
  <em>Extend the functionality of morecantile with additional commands.</em>
</p>
<p align="center">
  <a href="https://github.com/developmentseed/supermorecado/actions?query=workflow%3ACI" target="_blank">
      <img src="https://github.com/developmentseed/supermorecado/workflows/CI/badge.svg" alt="Test">
  </a>
  <a href="https://codecov.io/gh/developmentseed/supermorecado" target="_blank">
      <img src="https://codecov.io/gh/developmentseed/supermorecado/branch/main/graph/badge.svg" alt="Coverage">
  </a>
  <a href="https://pypi.org/project/supermorecado" target="_blank">
      <img src="https://img.shields.io/pypi/v/supermorecado?color=%2334D058&label=pypi%20package" alt="Package version">
  </a>
  <a href="https://pypistats.org/packages/supermorecado" target="_blank">
      <img src="https://img.shields.io/pypi/dm/supermorecado.svg" alt="Downloads">
  </a>
  <a href="https://github.com/developmentseed/supermorecado/blob/main/LICENSE" target="_blank">
      <img src="https://img.shields.io/github/license/developmentseed/supermorecado.svg" alt="License">
  </a>
</p>

---

**Documentation**: <a href="https://developmentseed.org/supermorecado/" target="_blank">https://developmentseed.org/supermorecado/</a>

**Source Code**: <a href="https://github.com/developmentseed/supermorecado" target="_blank">https://github.com/developmentseed/supermorecado</a>

---

supermorecado is like [supermercado](https://github.com/mapbox/supermercado), but with support for other TileMatrixSet grids.


## Install

```bash
$ python -m pip install -U pip
$ python -m pip install supermorecado

# Or install from source:

$ python -m pip install -U pip
$ python -m pip install git+https://github.com/developmentseed/supermorecado.git
```

## Usage

```
supermorecado --help
Usage: supermorecado [OPTIONS] COMMAND [ARGS]...

  Command line interface for the Supermorecado Python package.

Options:
  --help  Show this message and exit.

Commands:
  burn   Burn a stream of GeoJSONs into a output stream of the tiles they intersect for a given zoom.
  edges  For a stream of [<x>, <y>, <z>] tiles, return only those tiles that are on the edge.
  union  Returns the unioned shape of a stream of [<x>, <y>, <z>] tiles in GeoJSON.
```

### `supermorecado burn`

```
<{geojson} stream> | supermorecado burn <zoom> --identifier {tms Identifier} | <[x, y, z] stream>
```

Takes an input stream of GeoJSON and returns a stream of intersecting `[x, y, z]`s for a given zoom.

Using default TMS (`WebMercatorQuad`)
```
cat tests/fixtures/france.geojson | supermorecado burn 9 | morecantile shapes | fio collect | geojsonio
```

![](https://user-images.githubusercontent.com/10407788/236114524-c0a3543f-dfa3-4fd3-af2f-27d60ab897e1.jpg)

Using other TMS (e.g `WGS1984Quad`)
```
cat tests/fixtures/france.geojson | supermorecado burn 6 --identifier WGS1984Quad | morecantile shapes --identifier WGS1984Quad | fio collect | geojsonio
```

![](https://user-images.githubusercontent.com/10407788/236115182-441b1e23-3335-4392-9a72-4c98838c76de.jpg)

### `supermorecado edges`

```
<[x, y, z] stream> | supermorecado edges | <[x, y, z] stream>
```

Outputs a stream of `[x, y, z]`s representing the edge tiles of an input stream of `[x, y, z]`s. Edge tile = any tile that is either directly adjacent to a tile that does not exist, or diagonal to an empty tile.

```
cat tests/fixtures/france.geojson | supermorecado burn 9 | supermorecado edges | morecantile shapes | fio collect | geojsonio
```

![](https://user-images.githubusercontent.com/10407788/236123127-cc99c887-de9d-4823-a935-bd31a99809a2.jpg)

### `supermorecado union`

```
<[x, y, z] stream> | supermorecado union --identifier {tms Identifier} | <{geojson} stream>
```

Outputs a stream of unioned GeoJSON from an input stream of `[x, y, z]`s. Like `morecantile shapes` but as an overall footprint instead of individual shapes for each tile.

Using default TMS (`WebMercatorQuad`)
```
cat tests/fixtures/france.geojson | supermorecado burn 9 | supermorecado union | fio collect | geojsonio
```

![](https://user-images.githubusercontent.com/10407788/236115745-9c2f4fa3-e2ea-47d5-a5f5-c77f5308f4a3.jpg)

Using other TMS (e.g `WGS1984Quad`)

```
cat tests/fixtures/france.geojson | supermorecado burn 6 --identifier WGS1984Quad |  supermorecado union --identifier WGS1984Quad | fio collect | geojsonio
```

![](https://user-images.githubusercontent.com/10407788/236115946-2dfabe05-e51d-473b-9957-26bbbe9e61bb.jpg)

**Note**: We did not implement the `edges` CLI because `supermercado` method can be used (there is no TMS option to be used).

## Changes

See [CHANGES.md](https://github.com/developmentseed/supermorecado/blob/main/CHANGES.md).

## Contribution & Development

See [CONTRIBUTING.md](https://github.com/developmentseed/supermorecado/blob/main/CONTRIBUTING.md)

## License

See [LICENSE](https://github.com/developmentseed/supermorecado/blob/main/LICENSE)

## Authors

Created by [Development Seed](<http://developmentseed.org>)
