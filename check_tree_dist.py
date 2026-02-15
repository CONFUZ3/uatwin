import geopandas as gpd
import pandas as pd
import numpy as np

try:
    gdf = gpd.read_file('web_app/data/ua_trees.geojson')
    print(f"Total Trees: {len(gdf)}")
    print(f"Overall Bounds: {gdf.total_bounds}")
    
    # Analyze distribution
    # Bin coordinates to see if they are clustered
    gdf['lon_bin'] = (gdf.geometry.x * 100).astype(int)
    gdf['lat_bin'] = (gdf.geometry.y * 100).astype(int)
    
    counts = gdf.groupby(['lon_bin', 'lat_bin']).size()
    print("\nSpatial Distribution (clusters):")
    print(counts.sort_values(ascending=False).head(10))
    
    # Check if we have multiple distinct clusters or just one
    unique_locs = len(counts)
    print(f"\nNumber of populated 1km grid cells (approx): {unique_locs}")
    
    # detailed sample
    print("\nSample coordinates:")
    print(gdf.geometry.head(10))
    print(gdf.geometry.tail(10))

except Exception as e:
    print(e)
