from geoalchemy2.shape import to_shape
from shapely.geometry import shape, mapping
from shapely.wkt import loads as load_wkt, dumps as dump_wkt
from shapely.wkb import loads as load_wkb


def geojson_to_wkt(geojson):
    """Converts GeoJSON to WKT."""
    shapely_geom = shape(geojson)
    return dump_wkt(shapely_geom)


def wkt_to_geojson(wkt_str):
    """Converts WKT to GeoJSON."""
    shapely_geom = load_wkt(wkt_str)
    return mapping(shapely_geom)


def wkb_to_geojson(wkb_data):
    """Converts WKB to GeoJSON."""
    # check if input is WKBElement
    if hasattr(wkb_data, "data"):
        wkb_bytes = wkb_data.data
    else:
        wkb_bytes = wkb_data
    shapely_geom = load_wkb(wkb_bytes)
    return mapping(shapely_geom)


def wkb_to_wkt(wkb_data):
    """Converts WKB to WKT."""
    shapely_geom = load_wkb(wkb_data)
    return shapely_geom.wkt


def wkb_element_to_wkt(wkb_element):
    """Converts a GeoAlchemy WKBElement to WKT using Shapely."""
    shapely_geom = to_shape(wkb_element)
    return shapely_geom.wkt
