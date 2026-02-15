"""
Convert processed building data to optimized GeoJSON format for web use.
"""

import geopandas as gpd
import json
from pathlib import Path

def optimize_geojson(input_path, output_path, simplify_tolerance=0.0001):
    """
    Convert and optimize GeoJSON for web use.
    
    Args:
        input_path: Path to input GeoJSON
        output_path: Path to save optimized GeoJSON
        simplify_tolerance: Tolerance for geometry simplification
    """
    print(f"Loading GeoJSON from {input_path}...")
    gdf = gpd.read_file(input_path)
    
    print(f"Original: {len(gdf)} features")
    
    # Simplify geometries to reduce file size
    if simplify_tolerance > 0:
        print(f"Simplifying geometries (tolerance: {simplify_tolerance})...")
        gdf['geometry'] = gdf['geometry'].simplify(simplify_tolerance, preserve_topology=True)
    
    # Ensure CRS is WGS84 (EPSG:4326) for web use
    if gdf.crs is None:
        gdf.set_crs('EPSG:4326', inplace=True)
    elif gdf.crs != 'EPSG:4326':
        gdf = gdf.to_crs('EPSG:4326')
    
    # Select only necessary columns for web
    columns_to_keep = ['name', 'building_type', 'purpose', 'height', 'color', 'geometry']
    available_columns = [col for col in columns_to_keep if col in gdf.columns]
    gdf_optimized = gdf[available_columns]
    
    print(f"Saving optimized GeoJSON to {output_path}...")
    gdf_optimized.to_file(output_path, driver='GeoJSON')
    
    print(f"Optimized GeoJSON saved with {len(gdf_optimized)} features")
    return gdf_optimized

def main():
    """Main function"""
    data_dir = Path(__file__).parent.parent / "web_app" / "data"
    
    # Try different input files in order of preference
    input_files = [
        "buildings_with_heights.geojson",
        "buildings_enriched.geojson",
        "buildings_raw.geojson"
    ]
    
    input_path = None
    for filename in input_files:
        path = data_dir / filename
        if path.exists():
            input_path = path
            break
    
    if input_path is None:
        print("Error: No building data found. Run data acquisition scripts first.")
        return
    
    output_path = data_dir / "buildings.geojson"
    optimize_geojson(input_path, output_path)
    
    return output_path

if __name__ == "__main__":
    main()

