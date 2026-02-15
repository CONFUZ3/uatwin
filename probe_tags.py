import warnings
warnings.filterwarnings('ignore')
import osmnx as ox
import json
import geopandas as gpd

def probe():
    with open('config.json') as f:
        cfg = json.load(f)
    b = cfg['campus']['bounding_box']
    west, south, east, north = b['west'], b['south'], b['east'], b['north']
    print(f"BBox: {west}, {south}, {east}, {north}")

    tags_to_check = {
        "landuse": ["education", "commercial", "residential", "retail", "grass", "religious", "civic"],
        "leisure": ["park", "garden", "pitch", "track", "sports_centre"],
        "amenity": ["university", "school", "college", "parking"],
        "natural": ["wood", "scrub", "heath", "grassland"]
    }

    print("\n--- PROBING OSM TAGS ---")
    
    for key, values in tags_to_check.items():
        for v in values:
            try:
                gdf = ox.features_from_bbox(bbox=(west, south, east, north), tags={key: v})
                # Filter for polygons
                gdf = gdf[gdf.geometry.geom_type.isin(['Polygon', 'MultiPolygon'])]
                count = len(gdf)
                if count > 0:
                    print(f"{key}={v}: {count} polygons")
            except Exception as e:
                pass

if __name__ == "__main__":
    probe()
