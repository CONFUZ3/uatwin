"""
Fetch road and path network from OpenStreetMap via OSMnx.
Classifies into major roads, pedestrian/bike paths, and service roads.

Output: web_app/data/ua_roads.geojson
"""

import warnings
warnings.filterwarnings('ignore')

import json
from pathlib import Path


def fetch_roads():
    """Fetch road/path network for the UA campus from OSM."""
    import osmnx as ox
    import geopandas as gpd

    # Load config
    config_path = Path(__file__).parent.parent / "config.json"
    with open(config_path, "r") as f:
        config = json.load(f)

    b = config["campus"]["bounding_box"]
    west, south, east, north = b["west"], b["south"], b["east"], b["north"]

    print("Fetching road / path network …")

    tags = {"highway": True}

    try:
        gdf = ox.features_from_bbox(bbox=(west, south, east, north), tags=tags)
        # Keep line geometries only (roads are lines)
        gdf = gdf[gdf.geometry.geom_type.isin(["LineString", "MultiLineString"])].copy()
        print(f"  Fetched {len(gdf)} road/path segments")
    except Exception as e:
        print(f"  [ERROR] Road fetch failed: {e}")
        gdf = gpd.GeoDataFrame(columns=["geometry"], crs="EPSG:4326")

    if len(gdf) == 0:
        print("  [WARN] No roads found.")
        gdf = gpd.GeoDataFrame(columns=["geometry", "road_class"], crs="EPSG:4326")
        _save(gdf)
        return gdf

    # Classify roads
    major = {"primary", "secondary", "tertiary", "trunk", "motorway",
             "primary_link", "secondary_link", "tertiary_link", "trunk_link"}
    pedestrian = {"footway", "path", "pedestrian", "cycleway", "steps",
                  "bridleway", "corridor", "track"}
    service_types = {"service", "living_street"}

    def classify(row):
        hw = row.get("highway", "")
        if isinstance(hw, list):
            hw = hw[0] if hw else ""
        hw = str(hw).lower()
        if hw in major:
            return "major"
        if hw in pedestrian:
            return "pedestrian"
        if hw in service_types:
            return "service"
        if hw in ("residential", "unclassified"):
            return "residential"
        return "other"

    gdf["road_class"] = gdf.apply(classify, axis=1)

    # Keep useful columns
    keep = ["geometry", "road_class"]
    for col in ["name", "highway", "surface", "lanes", "maxspeed", "lit", "sidewalk"]:
        if col in gdf.columns:
            keep.append(col)
    gdf = gdf[keep].reset_index(drop=True)
    gdf["layer_type"] = "road"

    if gdf.crs is None:
        gdf.set_crs("EPSG:4326", inplace=True)

    print(f"  Classification: {gdf['road_class'].value_counts().to_dict()}")

    _save(gdf)
    return gdf


def _save(gdf):
    output_dir = Path(__file__).parent.parent / "web_app" / "data"
    output_dir.mkdir(parents=True, exist_ok=True)
    out = output_dir / "ua_roads.geojson"
    gdf.to_file(out, driver="GeoJSON")
    print(f"  [OK] Saved {len(gdf)} road segments → {out}")


if __name__ == "__main__":
    fetch_roads()
    print("\n[DONE] Roads fetched.")
