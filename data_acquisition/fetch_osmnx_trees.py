"""
Fetch tree and vegetation data from OpenStreetMap via OSMnx.
Queries natural=tree, natural=wood, natural=tree_row tags
within the University of Alabama campus boundary.
"""

import warnings
warnings.filterwarnings('ignore')

from pathlib import Path

def fetch_trees():
    """Fetch trees on and around the UA campus from OSM."""
    import osmnx as ox
    import geopandas as gpd
    from shapely.geometry import box
    
    # Load config
    import json
    config_path = Path(__file__).parent.parent / "config.json"
    with open(config_path, "r") as f:
        config = json.load(f)
        
    place_name = config["campus"]["name"]
    bbox_cfg = config["campus"]["bounding_box"]
    
    print(f"Fetching trees for: {place_name}")
    
    tags = {
        "natural": ["tree", "wood", "tree_row", "scrub"],
        "landuse": ["forest", "orchard", "meadow", "grass", "greenfield", "village_green", "recreation_ground"],
        "leisure": ["park", "garden"]
    }
    
    try:
        # Try finding by place first, but if it fails or if we prefer bbox control
        # Actually, let's prioritize bbox to match buildings exactly if place is too small/different
        # The user's issue was "dataset is not on the right extent", implying they want EXACT control.
        # So let's fallback to bbox immediately or just use bbox.
        # Let's try bbox primary for consistency with overture.
        west, south, east, north = bbox_cfg["west"], bbox_cfg["south"], bbox_cfg["east"], bbox_cfg["north"]
        print(f"  Using configured bbox: {west}, {south}, {east}, {north}")
        
        trees_gdf = ox.features_from_bbox(
            bbox=(west, south, east, north),
            tags=tags
        )
        print(f"  [OK] Fetched {len(trees_gdf)} tree/vegetation features via bbox")

    except Exception as e:
        print(f"  [WARN] Bbox query failed ({e}), trying place name as backup...")
        try:
            trees_gdf = ox.features_from_place(place_name, tags=tags)
            print(f"  [OK] Fetched {len(trees_gdf)} tree/vegetation features via place name")
        except Exception as e2:
            print(f"  [WARN] No trees found ({e2}). Creating empty file.")
            trees_gdf = gpd.GeoDataFrame(columns=['geometry'], crs='EPSG:4326')

    # Variable for bbox fallback in catch block not needed as we did bbox first
    # But for compatibility with existing structure if we kept the try/catch order:
    # logic updated above.
    
    # Existing code below expects trees_gdf
    pass 
    
    # Convert any polygon features (wood/forest) to centroids for simpler rendering
    # Keep point features as-is
    output_rows = []
    for idx, row in trees_gdf.iterrows():
        geom = row.geometry
        if geom is None:
            continue
        if geom.geom_type == 'Point':
            output_rows.append({'geometry': geom, 'type': 'tree'})
        elif geom.geom_type in ('Polygon', 'MultiPolygon'):
            # For wood/forest areas, scatter points within the polygon
            # to simulate tree density
            area = geom.area * 111000 * 111000  # rough sq meters
            
            # ADAPTIVE DENSITY
            # Default density (medium)
            density_m2 = 100 
            
            # High density for woods/forests
            if row.get('natural') in ['wood', 'scrub'] or row.get('landuse') in ['forest', 'orchard']:
                density_m2 = 50
            # Low density for fields/recreation
            elif row.get('landuse') in ['recreation_ground', 'meadow', 'grass', 'greenfield', 'village_green']:
                density_m2 = 200
            elif row.get('leisure') in ['park', 'garden']:
                density_m2 = 100
                
            n_points = max(1, int(area / density_m2))
            
            # Cap at 2000 per feature to prevent browser crash
            n_points = min(n_points, 2000)
            
            import numpy as np
            minx, miny, maxx, maxy = geom.bounds
            count = 0
            attempts = 0
            while count < n_points and attempts < n_points * 10:
                from shapely.geometry import Point
                px = np.random.uniform(minx, maxx)
                py = np.random.uniform(miny, maxy)
                pt = Point(px, py)
                if geom.contains(pt):
                    output_rows.append({'geometry': pt, 'type': 'tree'})
                    count += 1
                attempts += 1
        elif geom.geom_type == 'LineString':
            # tree_row — interpolate points along the line
            length_deg = geom.length
            length_m = length_deg * 111000
            n_points = max(2, int(length_m / 10))  # tree every ~10m
            n_points = min(n_points, 30)
            for i in range(n_points):
                frac = i / max(n_points - 1, 1)
                pt = geom.interpolate(frac, normalized=True)
                output_rows.append({'geometry': pt, 'type': 'tree'})
    
    if output_rows:
        import geopandas as gpd
        output_gdf = gpd.GeoDataFrame(output_rows, crs='EPSG:4326')
    else:
        output_gdf = gpd.GeoDataFrame(columns=['geometry', 'type'], crs='EPSG:4326')
    
    # Save
    output_dir = Path(__file__).parent.parent / "web_app" / "data"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "ua_trees.geojson"
    
    output_gdf.to_file(output_path, driver="GeoJSON")
    print(f"  [OK] Saved {len(output_gdf)} tree points to {output_path}")
    
    return output_gdf

if __name__ == "__main__":
    fetch_trees()
