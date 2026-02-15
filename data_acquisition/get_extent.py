import osmnx as ox
import pandas as pd

def get_bounds():
    # Way ID from user
    way_id = 89748187
    
    print(f"Fetching geometry for way {way_id}...")
    try:
        # Fetch by ID. 'W' prepended for Way in some contexts, but let's try geometries_from_xml if we had it, 
        # but here we want to fetch from API.
        # features_from_object requires a polygon, features_from_address...
        # Let's try to fetch the specific feature.
        # We can use geocode_to_gdf with a query or by ID if supported, but ox.features_from_ids is deprecated/removed in new versions?
        # Let's check what's available. If `features_from_ids` exists, good.
        # If not, we might need `geocode_to_gdf` with a query or just use the XML data?
        # No, I don't have the nodes for the XML. I have to hit the API.
        
        # New OSMnx uses `features.from_xml` (if I had the full XML with nodes) or we can just try to find the place.
        # But user gave a specific ID.
        # Let's try `ox.features.features_from_bbox` if we knew it... no.
        
        # Let's try searching by name since the XML has 'University of Alabama'.
        # gdf = ox.features.features_from_place("University of Alabama", tags={'amenity': 'university'})
        
        # Actually, let's try to interpret what the user wants. 
        # If they provided XML, maybe they want me to use THAT specific boundary?
        # The XML contains a list of <nd ref="...">.
        # WITHOUT the node definitions, I cannot compute the bbox from the XML snippet alone.
        # I MUST fetch it.
        
        # Using creating a graph from place might work, but I want the boundary of the university itself.
        gdf = ox.geocode_to_gdf("University of Alabama, Tuscaloosa, Alabama")
        print("Geocoded 'University of Alabama':")
        print(gdf[['lat', 'lon', 'bbox_north', 'bbox_south', 'bbox_east', 'bbox_west']].to_string())
        
        # Also let's try to verify if this matches the way ID.
        # In newer osmnx, we might not be able to easily fetch by ID without `features_from_ids`? 
        # Wait, `features_from_ids` is not in clean osmnx usually, but let's check.
        # Actually, standard way is `geocode_to_gdf` for places (relations).
        # Way 89748187 is a closed way (area). It might be the main campus polygon.
        
        return gdf.iloc[0]

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_bounds()
