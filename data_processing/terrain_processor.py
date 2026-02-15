"""
Process elevation data into terrain mesh for Three.js.
"""

import json
import numpy as np
from pathlib import Path

def create_terrain_mesh(elevation_data):
    """
    Create terrain mesh from elevation data.
    
    Args:
        elevation_data: Dictionary with elevation data
    
    Returns:
        Dictionary with terrain mesh data
    """
    elevation = np.array(elevation_data['elevation'])
    bounds = elevation_data['bounds']
    resolution = elevation_data['resolution']
    
    height, width = resolution['height'], resolution['width']
    
    # Create grid of coordinates
    lon_range = bounds['east'] - bounds['west']
    lat_range = bounds['north'] - bounds['south']
    
    # Convert to approximate meters
    lat_center = (bounds['north'] + bounds['south']) / 2
    lon_to_m = 111000 * np.cos(np.radians(lat_center))
    lat_to_m = 111000
    
    vertices = []
    faces = []
    uvs = []
    
    # Normalize elevation to 0-1 range for scaling
    min_elev = elevation_data['min_elevation']
    max_elev = elevation_data['max_elevation']
    elev_range = max_elev - min_elev if max_elev > min_elev else 1
    
    # Create vertices
    for i in range(height):
        for j in range(width):
            # Calculate position
            lon = bounds['west'] + (j / (width - 1)) * lon_range
            lat = bounds['south'] + (i / (height - 1)) * lat_range
            
            # Convert to local coordinates (meters)
            x = (lon - bounds['west']) * lon_to_m
            y = (lat - bounds['south']) * lat_to_m
            z = (elevation[i, j] - min_elev) / elev_range * 10  # Scale elevation
            
            vertices.append([x, y, z])
            uvs.append([j / (width - 1), 1 - i / (height - 1)])  # Flip V coordinate
    
    # Create faces (triangles)
    for i in range(height - 1):
        for j in range(width - 1):
            # Get indices
            idx = i * width + j
            idx_right = i * width + (j + 1)
            idx_bottom = (i + 1) * width + j
            idx_bottom_right = (i + 1) * width + (j + 1)
            
            # Two triangles per quad
            # Triangle 1
            faces.append([idx, idx_right, idx_bottom])
            # Triangle 2
            faces.append([idx_right, idx_bottom_right, idx_bottom])
    
    return {
        'vertices': vertices,
        'faces': faces,
        'uvs': uvs,
        'bounds': bounds,
        'resolution': resolution,
        'min_elevation': float(min_elev),
        'max_elevation': float(max_elev)
    }

def main():
    """Main function"""
    data_dir = Path(__file__).parent.parent / "web_app" / "data"
    input_path = data_dir / "terrain.json"
    
    if not input_path.exists():
        print(f"Error: {input_path} not found. Run fetch_elevation_data.py first.")
        return
    
    print("Loading elevation data...")
    with open(input_path, 'r') as f:
        elevation_data = json.load(f)
    
    print("Creating terrain mesh...")
    terrain_mesh = create_terrain_mesh(elevation_data)
    
    output_path = data_dir / "terrain_mesh.json"
    with open(output_path, 'w') as f:
        json.dump(terrain_mesh, f, indent=2)
    
    print(f"Saved terrain mesh to {output_path}")
    print(f"  Vertices: {len(terrain_mesh['vertices'])}")
    print(f"  Faces: {len(terrain_mesh['faces'])}")
    
    return terrain_mesh

if __name__ == "__main__":
    main()

