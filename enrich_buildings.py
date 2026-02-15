import geopandas as gpd
import pandas as pd
import osmnx as ox
from pathlib import Path

def enrich():
    print("Loading existing buildings...")
    existing_path = "web_app/data/ua_buildings.geojson"
    try:
        buildings_gdf = gpd.read_file(existing_path)
    except Exception as e:
        print(f"Failed to load {existing_path}: {e}")
        return

    print(f"Loaded {len(buildings_gdf)} buildings.")
    print(f"Columns: {buildings_gdf.columns.tolist()}")
    
    # Get bbox from data bounds
    bounds = buildings_gdf.total_bounds
    # minx, miny, maxx, maxy
    bbox = (bounds[0], bounds[1], bounds[2], bounds[3])
    print(f"Bounding box: {bbox}")

    print("Fetching OSM buildings...")
    tags = {'building': True}
    
    try:
        # Increase timeout if possible, but osmnx handles it
        ox.settings.timeout = 30
        
        osm_gdf = ox.features_from_bbox(bbox=bbox, tags=tags)
        print(f"Fetched {len(osm_gdf)} OSM features.")
        
        # Filter columns
        osm_cols = ['name', 'addr:housename', 'official_name', 'alt_name']
        available = [c for c in osm_cols if c in osm_gdf.columns]
        
        if not available:
            print("No name columns in OSM data.")
            return

        osm_gdf = osm_gdf[available + ['geometry']].copy()
        if osm_gdf.crs != buildings_gdf.crs:
            osm_gdf = osm_gdf.to_crs(buildings_gdf.crs)

        print("Merging...")
        enriched = gpd.sjoin(buildings_gdf, osm_gdf, how='left', predicate='intersects')
        
        print(f"Enriched columns: {enriched.columns.tolist()}")

        def get_best_name(row):
            if pd.notna(row.get('display_name')) and row['display_name'] != '':
                return row['display_name']
            if pd.notna(row.get('name')):
                return row['name']
            if pd.notna(row.get('addr:housename')):
                return row['addr:housename']
            for c in ['official_name', 'alt_name']:
                if c in row and pd.notna(row[c]):
                    return row[c]
            return None

        enriched['new_name'] = enriched.apply(get_best_name, axis=1)
        
        # Deduplicate by ID
        # If 'id' key error, check for id_left
        group_col = 'id'
        if 'id' not in enriched.columns and 'id_left' in enriched.columns:
            group_col = 'id_left'
            
        print(f"Grouping by {group_col}")
        name_map = enriched.groupby(group_col)['new_name'].first()
        
        # Apply names to original dataframe
        # We need to ensure we map back correctly.
        # If group_col is id_left, the index of name_map is the original ID.
        # If buildings_gdf index is NOT the ID, we need to map column to column.
        
        # Let's use map on the 'id' column of buildings_gdf
        if 'id' in buildings_gdf.columns:
             buildings_gdf['display_name'] = buildings_gdf['id'].map(name_map).fillna(buildings_gdf['display_name'])
        else:
             # Fallback to index if no ID column (shouldn't happen based on logs)
             buildings_gdf['display_name'] = name_map

        # --- Manual Metadata Enrichment ---
        print("Applying manual metadata for key buildings...")
        building_metadata = {
            "Bryant-Denny Stadium": {
                "name": "Bryant-Denny Stadium",
                "type": "stadium",
                "purpose": "Football Stadium",
                "capacity": 101821,
                "height": 45.0,
                "color": "#e63946"  # Crimson
            },
            "Gorgas Library": {
                "name": "Amelia Gayle Gorgas Library",
                "type": "library",
                "purpose": "Main Library",
                "height": 30.0,
                "color": "#a8dadc"
            },
            "Ferguson Center": {
                "name": "Ferguson Student Center",
                "type": "student_center",
                "purpose": "Student Services",
                "height": 25.0,
                "color": "#f1faee"
            },
            "Shelby Hall": {
                "name": "Shelby Hall",
                "type": "academic",
                "purpose": "Engineering & Science",
                "height": 28.0,
                "color": "#457b9d"
            },
            "Coleman Coliseum": {
                "name": "Coleman Coliseum",
                "type": "arena",
                "purpose": "Basketball/Gymnastics",
                "height": 22.0,
                "color": "#1d3557"
            },
            "Russell Hall": {
                "name": "Russell Hall",
                "type": "academic",
                "purpose": "Nursing/Health",
                "height": 20.0
            },
            "Gallalee Hall": {
                "name": "Gallalee Hall",
                "type": "academic",
                "purpose": "Physics",
                "height": 18.0
            }
        }

        def apply_metadata(row):
            name = row.get('display_name')
            if pd.isna(name): return row
            
            for key, data in building_metadata.items():
                if key.lower() in str(name).lower() or str(name).lower() in key.lower():
                    # Found a match!
                    row['display_name'] = data['name']
                    row['building_type'] = data.get('type', row.get('building_type'))
                    row['purpose'] = data.get('purpose', row.get('purpose'))
                    
                    # Optional: Override height if significantly different? 
                    # Overture height is usually better, so keep it unless missing.
                    if pd.isna(row.get('height')):
                         row['height'] = data.get('height')
                    
                    # Color (custom property for visualization)
                    if 'color' in data:
                        row['color'] = data['color']
                    return row
            return row

        # Apply metadata row by row
        buildings_gdf = buildings_gdf.apply(apply_metadata, axis=1)
        # ----------------------------------

        named_count = buildings_gdf['display_name'].notna().sum()
        print(f"New named count: {named_count} ({named_count/len(buildings_gdf):.1%})")

        out_path = "web_app/data/ua_buildings_enriched.geojson"
        buildings_gdf.to_file(out_path, driver="GeoJSON")
        print(f"Saved to {out_path}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    enrich()
