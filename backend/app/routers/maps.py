import os
import json
import random
import pandas as pd
import requests
from fastapi import APIRouter, HTTPException
from typing import Optional
from pydantic import BaseModel

router = APIRouter()

CSV_DIR = r"c:\Users\Admin\OneDrive\Desktop\KSP\catalyst_csv_bundle"
case_master_path = os.path.join(CSV_DIR, "CaseMaster.csv")
subhead_path = os.path.join(CSV_DIR, "CrimeSubHead.csv")
stations_json_path = r"c:\Users\Admin\OneDrive\Desktop\KSP\backend\geocoded_stations.json"

# In-memory stores
crime_df = None
police_stations = {}
cases_db = {}
subhead_map = {}

def load_map_data():
    global crime_df, police_stations, cases_db, subhead_map
    try:
        if os.path.exists(subhead_path):
            sh = pd.read_csv(subhead_path)
            for _, r in sh.iterrows():
                subhead_map[int(r['CrimeSubHeadID'])] = str(r['CrimeHeadName'])

        if os.path.exists(stations_json_path):
            with open(stations_json_path, 'r') as f:
                raw_stations = json.load(f)
                for k, v in raw_stations.items():
                    police_stations[int(k)] = v
            print(f"Loaded {len(police_stations)} REAL police stations from JSON.")

        df = pd.read_csv(case_master_path)
        df = df.dropna(subset=['latitude', 'longitude'])
        
        # Add crime category column for fast filtering
        df['CrimeCategory'] = df['CrimeMinorHeadID'].map(subhead_map).fillna("General Offense")
        df['Year'] = pd.to_datetime(df['CrimeRegisteredDate'], errors='coerce').dt.year.fillna(2025).astype(int)
        
        crime_df = df
        
        # Index cases for quick route lookup
        for _, row in df.iterrows():
            cases_db[int(row['CaseMasterID'])] = {
                'case_no': str(row.get('CrimeNo', row['CaseMasterID'])),
                'lat': float(row['latitude']),
                'lng': float(row['longitude']),
                'ps_id': int(row['PoliceStationID']) if pd.notnull(row.get('PoliceStationID')) else 1,
                'category': str(row['CrimeCategory']),
                'year': int(row['Year']),
                'facts': str(row.get('BriefFacts', ''))
            }
            
        print(f"Loaded {len(crime_df)} valid crime incidents for map mapping.")
    except Exception as e:
        print(f"Error loading map CSV data: {e}")

load_map_data()


@router.get("/stations")
def get_police_stations():
    """Returns list of geocoded police stations for map markers."""
    stations_list = []
    if os.path.exists(stations_json_path):
        try:
            with open(stations_json_path, 'r') as f:
                raw_stations = json.load(f)
                for ps_id, data in raw_stations.items():
                    stations_list.append({
                        "id": int(ps_id),
                        "name": data.get("name", f"Station #{ps_id}"),
                        "lat": data.get("lat"),
                        "lng": data.get("lng"),
                        "division": data.get("division", "BENGALURU CITY POLICE"),
                        "type": data.get("type", "Law & Order"),
                        "mobile": data.get("mobile", "9480801000"),
                        "email": data.get("email", "bcp.control@ksp.gov.in")
                    })
                return stations_list
        except Exception as e:
            print(f"Error reading stations json: {e}")

    for ps_id, data in police_stations.items():
        stations_list.append({
            "id": ps_id,
            "name": data.get("name", f"Station #{ps_id}"),
            "lat": data.get("lat"),
            "lng": data.get("lng"),
            "division": data.get("division", "BENGALURU CITY POLICE"),
            "type": data.get("type", "Law & Order"),
            "mobile": data.get("mobile", "9480801000"),
            "email": data.get("email", "bcp.control@ksp.gov.in")
        })
    return stations_list


@router.get("/hotspots")
def get_hotspots(crime_type: Optional[str] = None, year: Optional[int] = None):
    """Returns dynamic lat/lng/intensity array filtered by category and year."""
    if crime_df is None:
        return []
        
    filtered = crime_df
    
    if crime_type and crime_type.lower() != "all":
        filtered = filtered[filtered['CrimeCategory'].str.lower() == crime_type.lower()]
        
    if year and year > 0:
        filtered = filtered[filtered['Year'] == year]
        
    # Return lat/lng points (capped at 2500 for high-performance rendering)
    points = []
    for _, row in filtered.head(2500).iterrows():
        points.append([float(row['latitude']), float(row['longitude']), 1.0])
        
    return points


@router.get("/categories")
def get_crime_categories():
    """Returns available crime categories for map dropdown filter."""
    if crime_df is None:
        return ["All"]
    cats = ["All"] + sorted(crime_df['CrimeCategory'].unique().tolist())
    return cats


@router.get("/route")
def get_route(case_id: int):
    """Computes OSRM road polyline from nearest/assigned station to crime location."""
    if case_id not in cases_db:
        # Fallback to first available case ID
        case_id = list(cases_db.keys())[0]

    case_info = cases_db[case_id]
    ps_id = case_info['ps_id']
    
    if ps_id not in police_stations:
        # Find closest station geographically
        min_dist = float('inf')
        best_ps = list(police_stations.keys())[0]
        for sid, sdata in police_stations.items():
            d = (sdata['lat'] - case_info['lat'])**2 + (sdata['lng'] - case_info['lng'])**2
            if d < min_dist:
                min_dist = d
                best_ps = sid
        ps_id = best_ps
        
    ps_info = police_stations[ps_id]
    
    lon1, lat1 = ps_info['lng'], ps_info['lat']
    lon2, lat2 = case_info['lng'], case_info['lat']
    
    url = f"http://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}?overview=full&geometries=geojson"
    try:
        resp = requests.get(url, timeout=4)
        data = resp.json()
        if resp.status_code == 200 and 'routes' in data and len(data['routes']) > 0:
            coords = data['routes'][0]['geometry']['coordinates']
            duration = data['routes'][0]['duration']
            distance = data['routes'][0]['distance']
            path = [[c[1], c[0]] for c in coords] # lat, lon
            return {
                "case_id": case_id,
                "case_no": case_info['case_no'],
                "category": case_info['category'],
                "facts": case_info['facts'],
                "station": {
                    "id": ps_id,
                    "name": ps_info['name'],
                    "lat": lat1,
                    "lng": lon1,
                    "distance_km": round(distance / 1000.0, 2),
                    "duration_sec": round(duration, 0)
                },
                "crime_loc": [lat2, lon2],
                "station_loc": [lat1, lon1],
                "path": path
            }
    except Exception as e:
        print(f"OSRM error: {e}")
        
    # Straight-line fallback if OSRM offline
    return {
        "case_id": case_id,
        "case_no": case_info['case_no'],
        "category": case_info['category'],
        "station": {"id": ps_id, "name": ps_info['name'], "lat": lat1, "lng": lon1, "distance_km": 5.0, "duration_sec": 600},
        "crime_loc": [lat2, lon2],
        "station_loc": [lat1, lon1],
        "path": [[lat1, lon1], [lat2, lon2]]
    }


@router.post("/simulate_crime")
def simulate_crime():
    """Simulates a live emergency incident near NICE Road/Bengaluru outskirts & dispatches closest station."""
    # Pick a realistic location on Bengaluru outskirts (e.g. Uttarahalli / Hemmigepura / NICE Road)
    rand_lat = 12.8700 + random.uniform(-0.04, 0.04)
    rand_lng = 77.5100 + random.uniform(-0.04, 0.04)

    # Find closest station using Euclidean distance
    closest_ps_id = None
    min_dist = float('inf')
    
    for ps_id, ps_data in police_stations.items():
        dist = (ps_data['lat'] - rand_lat)**2 + (ps_data['lng'] - rand_lng)**2
        if dist < min_dist:
            min_dist = dist
            closest_ps_id = ps_id
            
    station = police_stations[closest_ps_id]
    
    lon1, lat1 = station['lng'], station['lat']
    lon2, lat2 = rand_lng, rand_lat
    
    url = f"http://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}?overview=full&geometries=geojson"
    try:
        resp = requests.get(url, timeout=4)
        data = resp.json()
        if resp.status_code == 200 and 'routes' in data and len(data['routes']) > 0:
            coords = data['routes'][0]['geometry']['coordinates']
            duration = data['routes'][0]['duration']
            distance = data['routes'][0]['distance']
            path = [[c[1], c[0]] for c in coords]
            return {
                "status": "DISPATCHED",
                "crime_loc": [rand_lat, rand_lng],
                "station": {
                    "id": closest_ps_id,
                    "name": station['name'],
                    "lat": station['lat'],
                    "lng": station['lng'],
                    "distance_km": round(distance / 1000.0, 2),
                    "duration_sec": round(duration, 0)
                },
                "path": path
            }
    except Exception as e:
        print(f"OSRM simulation error: {e}")
        
    return {
        "status": "DISPATCHED",
        "crime_loc": [rand_lat, rand_lng],
        "station": {"id": closest_ps_id, "name": station['name'], "lat": station['lat'], "lng": station['lng'], "distance_km": 4.5, "duration_sec": 540},
        "path": [[station['lat'], station['lng']], [rand_lat, rand_lng]]
    }
