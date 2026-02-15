"""
Load building footprints from manual dataset.
This script expects a GeoJSON file with building data to be placed in the data directory.
"""

import geopandas as gpd
import json
from pathlib import Path

def load_config():
    """Load configuration from config.json"""
    config_path = Path(__file__).parent.parent / "config.json"
    with open(config_path, 'r') as f:
        return json.load(f)

def load_manual_buildings(input_path):
    """
    Load building footprints from a manual GeoJSON file.
    
    Args:
        input_path: Path to the manual building GeoJSON file
    
    Returns:
        GeoDataFrame with building footprints
    """
    if not input_path.exists():
        raise FileNotFoundError(
            f"Building data file not found: {input_path}\n"
            f"Please place your building GeoJSON file at: {input_path}\n"
            f"See DATASET_REQUIREMENTS.md for format specifications."
        )
    
    print(f"Loading building data from {input_path}...")
    buildings = gpd.read_file(input_path)
    
    # Ensure CRS is set to WGS84 (EPSG:4326)
    if buildings.crs is None:
        buildings.set_crs('EPSG:4326', inplace=True)
        print("  [INFO] Set CRS to EPSG:4326 (WGS84)")
    elif buildings.crs != 'EPSG:4326':
        print(f"  [INFO] Converting CRS from {buildings.crs} to EPSG:4326")
        buildings = buildings.to_crs('EPSG:4326')
    
    print(f"  [OK] Loaded {len(buildings)} buildings")
    return buildings

def main():
    """Main function to load manual building data"""
    data_dir = Path(__file__).parent.parent / "web_app" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Look for manual building data file
    # User should place their building GeoJSON file here
    input_path = data_dir / "buildings_manual.geojson"
    
    try:
        buildings = load_manual_buildings(input_path)
    except FileNotFoundError as e:
        print(f"\n[ERROR] {e}")
        return None
    
    # Save to standard location for pipeline
    output_path = data_dir / "buildings_raw.geojson"
    print(f"\nSaving buildings to {output_path}...")
    buildings.to_file(output_path, driver='GeoJSON')
    print(f"[OK] Saved {len(buildings)} buildings")
    
    return buildings

if __name__ == "__main__":
    main()

