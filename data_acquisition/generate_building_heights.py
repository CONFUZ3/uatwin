"""
Generate or estimate building heights from available data.
"""

import geopandas as gpd
import json
import numpy as np
from pathlib import Path

def load_config():
    """Load configuration from config.json"""
    config_path = Path(__file__).parent.parent / "config.json"
    with open(config_path, 'r') as f:
        return json.load(f)

def estimate_building_height(building, default_height=15.0):
    """
    Estimate building height based on available data.
    
    Args:
        building: Building feature from GeoDataFrame
        default_height: Default height if estimation fails
    
    Returns:
        Estimated height in meters
    """
    # Check if height is already in the data
    if 'height' in building and building['height'] is not None:
        return float(building['height'])
    
    # Check for building:levels tag (common in OSM)
    if 'building:levels' in building and building['building:levels'] is not None:
        try:
            levels = float(building['building:levels'])
            # Assume ~3 meters per floor
            return levels * 3.0
        except (ValueError, TypeError):
            pass
    
    # Estimate based on building type
    building_type = building.get('building', 'unknown').lower()
    
    type_heights = {
        'stadium': 45.0,
        'university': 25.0,
        'dormitory': 20.0,
        'residential': 15.0,
        'commercial': 20.0,
        'industrial': 15.0,
        'warehouse': 12.0,
        'garage': 8.0,
        'house': 8.0,
        'apartments': 25.0
    }
    
    for btype, height in type_heights.items():
        if btype in building_type:
            return height
    
    # Estimate based on building area (larger buildings tend to be taller)
    if hasattr(building, 'geometry') and building.geometry is not None:
        area = building.geometry.area
        # Rough estimate: larger buildings might be taller
        if area > 10000:  # Large building
            return 30.0
        elif area > 5000:  # Medium building
            return 20.0
        elif area > 1000:  # Small building
            return 12.0
    
    return default_height

def assign_heights_to_buildings(buildings_gdf):
    """
    Assign heights to all buildings in the GeoDataFrame.
    
    Args:
        buildings_gdf: GeoDataFrame with building footprints
    
    Returns:
        GeoDataFrame with height column added/updated
    """
    config = load_config()
    default_height = config['building_defaults']['default_height']
    
    heights = []
    for idx, building in buildings_gdf.iterrows():
        height = estimate_building_height(building, default_height)
        heights.append(height)
    
    buildings_gdf['height'] = heights
    return buildings_gdf

def main():
    """Main function to generate building heights"""
    data_dir = Path(__file__).parent.parent / "web_app" / "data"
    input_path = data_dir / "buildings_enriched.geojson"
    
    # Fallback to raw if enriched doesn't exist
    if not input_path.exists():
        input_path = data_dir / "buildings_raw.geojson"
    
    if not input_path.exists():
        print(f"Error: Building data not found. Run fetch_osm_data.py first.")
        return
    
    print("Loading building data...")
    buildings = gpd.read_file(input_path)
    print(f"Loaded {len(buildings)} buildings")
    
    print("Estimating building heights...")
    buildings_with_heights = assign_heights_to_buildings(buildings)
    
    output_path = data_dir / "buildings_with_heights.geojson"
    print(f"Saving buildings with heights to {output_path}")
    
    # Remove color column if it exists (GeoJSON doesn't support list types)
    # Color is saved in metadata.json instead
    if 'color' in buildings_with_heights.columns:
        buildings_to_save = buildings_with_heights.drop(columns=['color'])
    else:
        buildings_to_save = buildings_with_heights
    
    buildings_to_save.to_file(output_path, driver='GeoJSON')
    
    # Print statistics
    heights = buildings_with_heights['height'].values
    print(f"\nHeight Statistics:")
    print(f"  Min: {heights.min():.1f}m")
    print(f"  Max: {heights.max():.1f}m")
    print(f"  Mean: {heights.mean():.1f}m")
    print(f"  Median: {np.median(heights):.1f}m")
    
    return buildings_with_heights

if __name__ == "__main__":
    main()

