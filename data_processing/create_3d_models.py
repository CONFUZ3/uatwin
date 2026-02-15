"""
Create 3D building models from footprints and heights.
Generates geometry data suitable for Three.js rendering.
"""

import geopandas as gpd
import json
import numpy as np
from pathlib import Path
from shapely.geometry import Polygon, Point

def load_config():
    """Load configuration from config.json"""
    config_path = Path(__file__).parent.parent / "config.json"
    with open(config_path, 'r') as f:
        return json.load(f)

def extrude_polygon(polygon, height):
    """
    Extrude a 2D polygon to create a 3D building.
    
    Args:
        polygon: Shapely Polygon
        height: Building height in meters
    
    Returns:
        Dictionary with vertices, faces, and normals
    """
    if polygon is None or polygon.is_empty:
        return None
    
    # Get exterior coordinates
    coords = list(polygon.exterior.coords)
    if len(coords) < 3:
        return None
    
    # Remove duplicate last point if present
    if coords[0] == coords[-1]:
        coords = coords[:-1]
    
    num_points = len(coords)
    vertices = []
    faces = []
    
    # Convert lat/lon to approximate meters (rough conversion for small area)
    # For UA campus, 1 degree ≈ 111,000 meters
    lat_center = polygon.centroid.y
    lon_to_m = 111000 * np.cos(np.radians(lat_center))
    lat_to_m = 111000
    
    # Create bottom face vertices
    bottom_vertices = []
    for lon, lat in coords:
        x = (lon - coords[0][0]) * lon_to_m
        y = (lat - coords[0][1]) * lat_to_m
        z = 0
        bottom_vertices.append([x, y, z])
        vertices.append([x, y, z])
    
    # Create top face vertices
    top_vertices = []
    for lon, lat in coords:
        x = (lon - coords[0][0]) * lon_to_m
        y = (lat - coords[0][1]) * lat_to_m
        z = height
        top_vertices.append([x, y, z])
        vertices.append([x, y, z])
    
    # Create side faces (walls)
    for i in range(num_points):
        next_i = (i + 1) % num_points
        # Each wall is a quad (two triangles)
        # Triangle 1
        faces.append([i, next_i, num_points + i])
        # Triangle 2
        faces.append([next_i, num_points + next_i, num_points + i])
    
    # Create bottom face (triangulated)
    if num_points > 2:
        for i in range(1, num_points - 1):
            faces.append([0, i, i + 1])
    
    # Create top face (triangulated)
    if num_points > 2:
        base = num_points
        for i in range(1, num_points - 1):
            faces.append([base, base + i + 1, base + i])
    
    return {
        'vertices': vertices,
        'faces': faces,
        'num_vertices': len(vertices),
        'num_faces': len(faces)
    }

def process_buildings_to_3d(buildings_gdf):
    """
    Process all buildings to 3D models.
    
    Args:
        buildings_gdf: GeoDataFrame with building footprints and heights
    
    Returns:
        List of 3D building models
    """
    buildings_3d = []
    
    for idx, building in buildings_gdf.iterrows():
        geometry = building.geometry
        
        # Get height
        height = building.get('height', 15.0)
        if height is None or height <= 0:
            height = 15.0
        
        # Handle different geometry types
        if geometry.geom_type == 'Polygon':
            model = extrude_polygon(geometry, height)
            if model:
                model['id'] = str(idx)
                model['name'] = building.get('name', f'Building {idx}')
                model['type'] = building.get('building_type', 'unknown')
                model['purpose'] = building.get('purpose', 'Unknown')
                model['height'] = float(height)
                model['color'] = building.get('color', [0.7, 0.7, 0.8])
                model['center'] = [geometry.centroid.x, geometry.centroid.y]
                buildings_3d.append(model)
        
        elif geometry.geom_type == 'MultiPolygon':
            # Handle multipolygon by processing each polygon
            for poly in geometry.geoms:
                model = extrude_polygon(poly, height)
                if model:
                    model['id'] = f"{idx}_{len(buildings_3d)}"
                    model['name'] = building.get('name', f'Building {idx}')
                    model['type'] = building.get('building_type', 'unknown')
                    model['purpose'] = building.get('purpose', 'Unknown')
                    model['height'] = float(height)
                    model['color'] = building.get('color', [0.7, 0.7, 0.8])
                    model['center'] = [poly.centroid.x, poly.centroid.y]
                    buildings_3d.append(model)
    
    return buildings_3d

def save_3d_models(buildings_3d, output_path):
    """
    Save 3D building models to JSON.
    
    Args:
        buildings_3d: List of 3D building models
        output_path: Path to save JSON file
    """
    output_data = {
        'buildings': buildings_3d,
        'count': len(buildings_3d),
        'metadata': {
            'format': '3d_buildings',
            'version': '1.0'
        }
    }
    
    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"Saved {len(buildings_3d)} 3D building models to {output_path}")

def main():
    """Main function"""
    data_dir = Path(__file__).parent.parent / "web_app" / "data"
    input_path = data_dir / "buildings.geojson"
    
    if not input_path.exists():
        print(f"Error: {input_path} not found. Run convert_to_geojson.py first.")
        return
    
    print("Loading building data...")
    buildings = gpd.read_file(input_path)
    print(f"Loaded {len(buildings)} buildings")
    
    print("Creating 3D models...")
    buildings_3d = process_buildings_to_3d(buildings)
    
    output_path = data_dir / "buildings_3d.json"
    save_3d_models(buildings_3d, output_path)
    
    return buildings_3d

if __name__ == "__main__":
    main()

