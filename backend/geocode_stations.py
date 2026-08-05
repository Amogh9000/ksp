import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import json
import os
import time

CSV_PATH = r"catalyst_csv_bundle\police_stations.csv"
OUT_PATH = r"geocoded_stations.json"

def main():
    print("Loading police stations CSV...")
    df = pd.read_csv(CSV_PATH)
    
    geolocator = Nominatim(user_agent="ksp_datathon_app")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1.5)
    
    results = {}
    
    print("Geocoding stations... (limiting to 20 for speed)")
    count = 0
    for _, row in df.iterrows():
        if count >= 10000:
            break
            
        station_name = str(row.get('Station', ''))
        # Clean up the name a bit to help geocoder
        name_parts = station_name.split(' ')
        clean_name = name_parts[0] + " Police Station, Bangalore"
        
        try:
            location = geolocator.geocode(clean_name)
            if location:
                # Use Sl as the ID since Station Code is sometimes empty
                ps_id = int(row['Sl'])
                results[ps_id] = {
                    "name": name_parts[0] + " Police Station",
                    "lat": location.latitude,
                    "lng": location.longitude
                }
                print(f"Found: {clean_name} -> {location.latitude}, {location.longitude}")
                count += 1
            else:
                print(f"Not found: {clean_name}")
        except Exception as e:
            print(f"Error on {clean_name}: {e}")
            
    with open(OUT_PATH, 'w') as f:
        json.dump(results, f, indent=4)
        
    print(f"Geocoded {len(results)} stations to {OUT_PATH}")

if __name__ == "__main__":
    main()
