"""
Load elevation data from manual dataset.
This script expects elevation data to be provided in JSON format.
"""

import json
import numpy as np
from pathlib import Path

def load_config():
    """Load configuration from config.json"""
    config_path = Path(__file__).parent.parent / "config.json"
    with open(config_path, 'r') as f:
        return json.load(f)

def load_manual_elevation(input_path):
    """
    Load elevation data from a manual JSON file.
    
    Args:
        input_path: Path to the manual elevation JSON file
    
    Returns:
        Dictionary with elevation data
    """
    if not input_path.exists():
        raise FileNotFoundError(
            f"Elevation data file not found: {input_path}\n"
            f"Please place your elevation JSON file at: {input_path}\n"
            f"See DATASET_REQUIREMENTS.md for format specifications."
        )
    
    print(f"Loading elevation data from {input_path}...")
    with open(input_path, 'r') as f:
        elevation_data = json.load(f)
    
    # Validate required fields
    required_fields = ['bounds', 'resolution', 'elevation']
    for field in required_fields:
        if field not in elevation_data:
            raise ValueError(f"Missing required field '{field}' in elevation data")
    
    print(f"  [OK] Loaded elevation data")
    print(f"  Resolution: {elevation_data['resolution']['height']}x{elevation_data['resolution']['width']}")
    
    return elevation_data

def main():
    """Main function to load manual elevation data"""
    data_dir = Path(__file__).parent.parent / "web_app" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Look for manual elevation data file
    # User should place their elevation JSON file here
    input_path = data_dir / "elevation_manual.json"
    
    try:
        elevation_data = load_manual_elevation(input_path)
    except FileNotFoundError as e:
        print(f"\n[ERROR] {e}")
        return None
    
    # Save to standard location for pipeline
    output_path = data_dir / "terrain.json"
    print(f"\nSaving elevation data to {output_path}...")
    with open(output_path, 'w') as f:
        json.dump(elevation_data, f, indent=2)
    print(f"[OK] Saved elevation data")
    
    return elevation_data

if __name__ == "__main__":
    main()

