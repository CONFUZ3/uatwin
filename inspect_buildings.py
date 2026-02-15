import geopandas as gpd
import pandas as pd

try:
    gdf = gpd.read_file('web_app/data/ua_buildings.geojson')
    print(f"Total Buildings: {len(gdf)}")
    if 'display_name' in gdf.columns:
        named_count = gdf['display_name'].notna().sum()
        print(f"Named Buildings: {named_count}")
        print(f"Percentage Named: {named_count/len(gdf)*100:.1f}%")
        print("\nStructure of first record:")
        print(gdf.iloc[0])
    else:
        print("Column 'display_name' not found in GeoJSON")
        print("Available columns:", gdf.columns)

except Exception as e:
    print(f"Error reading file: {e}")
