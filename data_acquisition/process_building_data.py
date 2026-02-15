"""
Process and enrich building data with names, purposes, and metadata.
"""

import json
import geopandas as gpd
from pathlib import Path

def load_config():
    """Load configuration from config.json"""
    config_path = Path(__file__).parent.parent / "config.json"
    with open(config_path, 'r') as f:
        return json.load(f)

def get_building_metadata():
    """
    Get known building metadata for University of Alabama.
    This would ideally come from a database or official source.
    """
    # Building metadata - can be expanded with official campus data
    building_metadata = {
        "Bryant-Denny Stadium": {
            "name": "Bryant-Denny Stadium",
            "type": "stadium",
            "purpose": "Football Stadium",
            "capacity": 101821,
            "height": 45.0,
            "color": [0.9, 0.1, 0.1]  # Crimson red
        },
        "Gorgas Library": {
            "name": "Amelia Gayle Gorgas Library",
            "type": "library",
            "purpose": "Main Library",
            "height": 30.0,
            "color": [0.7, 0.7, 0.8]
        },
        "Ferguson Center": {
            "name": "Ferguson Student Center",
            "type": "student_center",
            "purpose": "Student Services",
            "height": 25.0,
            "color": [0.8, 0.8, 0.7]
        }
    }
    return building_metadata

def enrich_buildings_with_metadata(buildings_gdf):
    """
    Enrich building GeoDataFrame with metadata.
    
    Args:
        buildings_gdf: GeoDataFrame with building footprints
    
    Returns:
        GeoDataFrame with enriched metadata
    """
    import pandas as pd
    
    metadata = get_building_metadata()
    config = load_config()
    
    # Initialize metadata columns if they don't exist
    if 'name' not in buildings_gdf.columns:
        buildings_gdf['name'] = None
    if 'building_type' not in buildings_gdf.columns:
        buildings_gdf['building_type'] = None
    if 'purpose' not in buildings_gdf.columns:
        buildings_gdf['purpose'] = None
    if 'height' not in buildings_gdf.columns:
        buildings_gdf['height'] = config['building_defaults']['default_height']
    if 'color' not in buildings_gdf.columns:
        default_color = config['building_defaults']['color']
        buildings_gdf['color'] = [default_color] * len(buildings_gdf)
    
    # Try to match buildings by name from OSM tags
    for idx, building in buildings_gdf.iterrows():
        # Check if building has a name in OSM tags
        building_name = None
        if 'name' in building and pd.notna(building['name']):
            building_name = building['name']
        elif 'addr:housename' in building and pd.notna(building['addr:housename']):
            building_name = building['addr:housename']
        
        # Match with known metadata
        if building_name:
            for known_name, known_data in metadata.items():
                if known_name.lower() in building_name.lower() or building_name.lower() in known_name.lower():
                    buildings_gdf.at[idx, 'name'] = known_data['name']
                    buildings_gdf.at[idx, 'building_type'] = known_data.get('type', 'unknown')
                    buildings_gdf.at[idx, 'purpose'] = known_data.get('purpose', 'Unknown')
                    buildings_gdf.at[idx, 'height'] = known_data.get('height', config['building_defaults']['default_height'])
                    buildings_gdf.at[idx, 'color'] = known_data.get('color', config['building_defaults']['color'])
                    break
        
        # Set default name if not found
        if pd.isna(buildings_gdf.at[idx, 'name']):
            buildings_gdf.at[idx, 'name'] = f"Building {idx}"
            buildings_gdf.at[idx, 'building_type'] = building.get('building', 'unknown')
            buildings_gdf.at[idx, 'purpose'] = 'Unknown'
    
    return buildings_gdf

def main():
    """Main function to process building data"""
    import pandas as pd
    
    data_dir = Path(__file__).parent.parent / "web_app" / "data"
    input_path = data_dir / "buildings_raw.geojson"
    output_path = data_dir / "buildings_enriched.geojson"
    
    if not input_path.exists():
        print(f"Error: {input_path} not found. Run fetch_osm_data.py first.")
        return
    
    print("Loading building data...")
    buildings = gpd.read_file(input_path)
    print(f"Loaded {len(buildings)} buildings")
    
    print("Enriching with metadata...")
    buildings_enriched = enrich_buildings_with_metadata(buildings)
    
    print(f"Saving enriched buildings to {output_path}")
    
    # Remove color column if it exists (GeoJSON doesn't support list types)
    # Color is saved in metadata.json instead
    if 'color' in buildings_enriched.columns:
        buildings_to_save = buildings_enriched.drop(columns=['color'])
    else:
        buildings_to_save = buildings_enriched
    
    buildings_to_save.to_file(output_path, driver='GeoJSON')
    
    # Also save metadata as separate JSON for easy access
    metadata_path = data_dir / "building_metadata.json"
    metadata_dict = {}
    for idx, building in buildings_enriched.iterrows():
        metadata_dict[str(idx)] = {
            "name": building.get('name', f"Building {idx}"),
            "type": building.get('building_type', 'unknown'),
            "purpose": building.get('purpose', 'Unknown'),
            "height": float(building.get('height', 15.0)),
            "color": building.get('color', [0.7, 0.7, 0.8])
        }
    
    with open(metadata_path, 'w') as f:
        json.dump(metadata_dict, f, indent=2)
    
    print(f"Saved metadata to {metadata_path}")
    return buildings_enriched

if __name__ == "__main__":
    main()

