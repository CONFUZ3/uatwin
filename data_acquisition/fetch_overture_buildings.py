"""
Fetch 3D building data from Overture Maps for the UA campus.
Uses the overturemaps Python package to stream building geometries
with height attributes from the cloud-hosted Parquet dataset.
"""

import json
from pathlib import Path


def fetch_buildings():
    """Fetch UA campus buildings from Overture Maps."""
    # Load config
    config_path = Path(__file__).parent.parent / "config.json"
    with open(config_path, "r") as f:
        config = json.load(f)

    bbox_cfg = config["campus"]["bounding_box"]
    # box(xmin, ymin, xmax, ymax)
    ua_bbox = (bbox_cfg["west"], bbox_cfg["south"], bbox_cfg["east"], bbox_cfg["north"])

    from overturemaps import core

    print(f"Fetching Overture Maps buildings for bbox: {ua_bbox}")
    buildings_gdf = core.geodataframe("building", bbox=ua_bbox)
    print(f"  [OK] Fetched {len(buildings_gdf)} buildings")

    # Extract height — Overture stores height as a numeric field
    # Some records may have None height; we assign a default
    if 'height' in buildings_gdf.columns:
        buildings_gdf['height'] = buildings_gdf['height'].fillna(8.0)
    else:
        buildings_gdf['height'] = 8.0

    # Extract a clean name from Overture's nested names structure
    def extract_name(row):
        names = row.get('names') if hasattr(row, 'get') else None
        if names is None:
            return None
        if isinstance(names, dict):
            return names.get('primary', None)
        if isinstance(names, list) and len(names) > 0:
            first = names[0]
            if isinstance(first, dict):
                return first.get('value', first.get('primary', None))
            return str(first)
        return None

    buildings_gdf['display_name'] = buildings_gdf.apply(extract_name, axis=1)

    # Extract building class/subtype if available
    for col in ['class', 'subtype']:
        if col not in buildings_gdf.columns:
            buildings_gdf[col] = None

    # Select columns for output
    keep_cols = ['id', 'height', 'display_name', 'class', 'subtype', 'geometry']
    available_cols = [c for c in keep_cols if c in buildings_gdf.columns]
    output_gdf = buildings_gdf[available_cols].copy()

    # Ensure CRS
    if output_gdf.crs is None:
        output_gdf.set_crs('EPSG:4326', inplace=True)

    # --- NEW: Enrich with OSM Data ---
    import osmnx as ox
    
    print("Fetching OSM buildings for name enrichment...")
    tags = {'building': True}
    try:
        # Fetch OSM buildings
        osm_gdf = ox.features_from_bbox(
            bbox=ua_bbox,
            tags=tags
        )
        
        # Filter to only relevant columns and ensure CRS matches
        osm_cols = ['name', 'addr:housename', 'official_name', 'alt_name']
        available_osm_cols = [c for c in osm_cols if c in osm_gdf.columns]
        
        if not available_osm_cols:
             print("  [WARN] No name columns found in OSM data.")
        else:
            osm_gdf = osm_gdf[available_osm_cols + ['geometry']].copy()
            if osm_gdf.crs != output_gdf.crs:
                osm_gdf = osm_gdf.to_crs(output_gdf.crs)

            # Spatial join: Overture (left) + OSM (right)
            # We want to keep all Overture buildings
            enriched = gpd.sjoin(
                output_gdf, 
                osm_gdf, 
                how='left', 
                predicate='intersects'
            )
            
            # Function to prioritize names
            def get_best_name(row):
                # 1. Keep existing Overture name if present
                if pd.notna(row['display_name']) and row['display_name'] != '':
                    return row['display_name']
                
                # 2. Try OSM 'name'
                if 'name' in row and pd.notna(row['name']):
                    return row['name']
                
                # 3. Try OSM 'addr:housename'
                if 'addr:housename' in row and pd.notna(row['addr:housename']):
                    return row['addr:housename']
                
                # 4. Try other variants
                for col in ['official_name', 'alt_name']:
                    if col in row and pd.notna(row[col]):
                        return row[col]
                        
                return None

            # Apply name selection
            enriched['new_display_name'] = enriched.apply(get_best_name, axis=1)
            
            # sjoin creates duplicates if multiple OSM features intersect one Overture feature.
            # We group by the Overture ID (which is in the index or 'id' col) and take the first valid name.
            # Since 'id' is a column, let's use it.
            
            # First, update display_name where we found a better one
            # We can't just assign back because of duplicates.
            # Let's create a mapping of id -> best_name
            
            # Sort to prioritize rows with names?
            # Actually, let's just drop duplicates keeping the one with a name if possible.
            # But the simplest way is to group by 'id' and take the first non-null new_display_name.
            
            name_map = enriched.groupby('id')['new_display_name'].first()
            
            # Map back to original output_gdf
            output_gdf['display_name'] = output_gdf['id'].map(name_map)
            
            print(f"  [OK] Merged with OSM data. {len(osm_gdf)} OSM features processed.")
            
    except Exception as e:
        print(f"  [WARN] OSM enrichment failed: {e}")
        import traceback
        traceback.print_exc()

    # ---------------------------------

    # Save
    output_dir = Path(__file__).parent.parent / "web_app" / "data"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "ua_buildings.geojson"

    output_gdf.to_file(output_path, driver="GeoJSON")
    print(f"  [OK] Saved {len(output_gdf)} buildings to {output_path}")
    named = output_gdf['display_name'].notna().sum()
    print(f"  Named buildings: {named}")
    print(f"  Height range: {output_gdf['height'].min():.1f} – {output_gdf['height'].max():.1f} m")

    return output_gdf


if __name__ == "__main__":
    fetch_buildings()
