import osmnx as ox
import geopandas as gpd

def check_center():
    # Campus center approx
    center_point = (33.2084, -87.5385)
    
    tags = {
        "landuse": True,
        "leisure": True,
        "natural": True,
        "amenity": True
    }
    
    print("Fetching features at campus center...")
    try:
        gdf = ox.features_from_point(center_point, tags=tags, dist=500)
        print(f"Found {len(gdf)} features.")
        if len(gdf) > 0:
            print(gdf[['landuse', 'leisure', 'natural', 'amenity', 'geometry']].head(20))
            
            # Count types
            print("\nTop tags:")
            print(gdf['landuse'].value_counts().head())
            print(gdf['leisure'].value_counts().head())
    except Exception as e:
        print(e)

if __name__ == "__main__":
    check_center()
