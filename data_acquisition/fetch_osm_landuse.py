"""
Fetch land-use features from OpenStreetMap via OSMnx.
Queries parking lots, green spaces, water features, and general landuse
polygons (education, residential, commercial, retail) to fill map gaps.

Outputs:
  - web_app/data/ua_parking.geojson
  - web_app/data/ua_greenspaces.geojson
  - web_app/data/ua_water.geojson
  - web_app/data/ua_landuse.geojson  <-- NEW: Base layer
"""

import warnings
warnings.filterwarnings('ignore')

import json
from pathlib import Path
import pandas as pd
import geopandas as gpd


def _load_bbox():
    config_path = Path(__file__).parent.parent / "config.json"
    with open(config_path, "r") as f:
        config = json.load(f)
    b = config["campus"]["bounding_box"]
    return b["west"], b["south"], b["east"], b["north"]


def _save(gdf, name):
    output_dir = Path(__file__).parent.parent / "web_app" / "data"
    output_dir.mkdir(parents=True, exist_ok=True)
    out = output_dir / name
    gdf.to_file(out, driver="GeoJSON")
    print(f"  [OK] Saved {len(gdf)} features → {out}")
    return out


def fetch_parking():
    """Fetch parking lots from OSM."""
    import osmnx as ox
    west, south, east, north = _load_bbox()
    print("Fetching parking lots …")

    tags = {"amenity": "parking"}
    try:
        gdf = ox.features_from_bbox(bbox=(west, south, east, north), tags=tags)
        gdf = gdf[gdf.geometry.geom_type.isin(["Polygon", "MultiPolygon"])].copy()
        
        keep = ["geometry"]
        for col in ["name", "surface", "capacity", "access", "fee"]:
            if col in gdf.columns:
                keep.append(col)
        gdf = gdf[keep].reset_index(drop=True)
        gdf["layer_type"] = "parking"
        print(f"  Found {len(gdf)} parking polygons")
    except Exception as e:
        print(f"  [WARN] Parking fetch failed: {e}")
        gdf = gpd.GeoDataFrame(columns=["geometry", "layer_type"], crs="EPSG:4326")

    if gdf.crs is None:
        gdf.set_crs("EPSG:4326", inplace=True)
    _save(gdf, "ua_parking.geojson")
    return gdf


def fetch_greenspaces():
    """Fetch parks, grass, gardens, sports pitches from OSM."""
    import osmnx as ox
    west, south, east, north = _load_bbox()
    print("Fetching green spaces …")

    all_frames = []
    # Expanded tags to catch more green areas
    tag_sets = [
        {"leisure": ["park", "garden", "pitch", "playground", "track", "nature_reserve"]},
        {"landuse": ["grass", "meadow", "recreation_ground", "village_green", "allotments", "cemetery"]},
        {"natural": ["grassland", "scrub", "wood", "heath"]},
    ]

    for tags in tag_sets:
        try:
            gdf = ox.features_from_bbox(bbox=(west, south, east, north), tags=tags)
            gdf = gdf[gdf.geometry.geom_type.isin(["Polygon", "MultiPolygon"])].copy()
            if len(gdf) > 0:
                keep = ["geometry"]
                for col in ["name", "leisure", "landuse", "natural", "sport"]:
                    if col in gdf.columns:
                        keep.append(col)
                all_frames.append(gdf[keep].reset_index(drop=True))
                print(f"    {tags}: {len(gdf)} polygons")
        except Exception as e:
            pass # Silent fail for empty sets

    if all_frames:
        combined = pd.concat(all_frames, ignore_index=True)
        combined = gpd.GeoDataFrame(combined, crs="EPSG:4326")
        combined = combined.drop_duplicates(subset="geometry").reset_index(drop=True)
    else:
        combined = gpd.GeoDataFrame(columns=["geometry"], crs="EPSG:4326")

    combined["layer_type"] = "greenspace"
    print(f"  Total green spaces: {len(combined)}")
    _save(combined, "ua_greenspaces.geojson")
    return combined


def fetch_general_landuse():
    """Fetch broad landuse polygons to fill gaps (education, residential, commercial)."""
    import osmnx as ox
    west, south, east, north = _load_bbox()
    print("Fetching general landuse (base layer) …")

    all_frames = []
    tag_sets = [
        {"landuse": ["education", "residential", "commercial", "retail", "civic", "religious"]},
        {"amenity": ["university", "school", "college", "hospital"]},
    ]

    for tags in tag_sets:
        try:
            gdf = ox.features_from_bbox(bbox=(west, south, east, north), tags=tags)
            gdf = gdf[gdf.geometry.geom_type.isin(["Polygon", "MultiPolygon"])].copy()
            if len(gdf) > 0:
                keep = ["geometry"]
                for col in ["name", "landuse", "amenity"]:
                    if col in gdf.columns:
                        keep.append(col)
                all_frames.append(gdf[keep].reset_index(drop=True))
                print(f"    {tags}: {len(gdf)} polygons")
        except Exception as e:
            pass

    if all_frames:
        combined = pd.concat(all_frames, ignore_index=True)
        combined = gpd.GeoDataFrame(combined, crs="EPSG:4326")
        combined = combined.drop_duplicates(subset="geometry").reset_index(drop=True)
    else:
        combined = gpd.GeoDataFrame(columns=["geometry"], crs="EPSG:4326")

    combined["layer_type"] = "landuse"
    print(f"  Total general landuse polygons: {len(combined)}")
    _save(combined, "ua_landuse.geojson")
    return combined


def fetch_water():
    """Fetch water bodies and waterways from OSM."""
    import osmnx as ox
    west, south, east, north = _load_bbox()
    print("Fetching water features …")

    all_frames = []
    tag_sets = [
        {"natural": "water"},
        {"waterway": True},
        {"water": True},
    ]

    for tags in tag_sets:
        try:
            gdf = ox.features_from_bbox(bbox=(west, south, east, north), tags=tags)
            if len(gdf) > 0:
                keep = ["geometry"]
                for col in ["name", "natural", "waterway", "water"]:
                    if col in gdf.columns:
                        keep.append(col)
                all_frames.append(gdf[keep].reset_index(drop=True))
                print(f"    {tags}: {len(gdf)} features")
        except Exception as e:
            pass

    if all_frames:
        combined = pd.concat(all_frames, ignore_index=True)
        combined = gpd.GeoDataFrame(combined, crs="EPSG:4326")
        combined = combined.drop_duplicates(subset="geometry").reset_index(drop=True)
    else:
        combined = gpd.GeoDataFrame(columns=["geometry"], crs="EPSG:4326")

    combined["layer_type"] = "water"
    print(f"  Total water features: {len(combined)}")
    _save(combined, "ua_water.geojson")
    return combined


if __name__ == "__main__":
    fetch_parking()
    fetch_greenspaces()
    fetch_water()
    fetch_general_landuse()
    print("\n[DONE] All land-use layers fetched.")
