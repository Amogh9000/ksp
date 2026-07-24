import os
import json
import pandas as pd
import networkx as nx
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/graph", tags=["Network Graph"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CSV_DIR = os.path.join(BASE_DIR, "catalyst_csv_bundle")
accused_path = os.path.join(CSV_DIR, "Accused.csv")
case_master_path = os.path.join(CSV_DIR, "CaseMaster.csv")
victim_path = os.path.join(CSV_DIR, "Victim.csv")
subhead_path = os.path.join(CSV_DIR, "CrimeSubHead.csv")
stations_path = os.path.join(BASE_DIR, "geocoded_stations.json")

# In-memory datasets
df_accused = None
df_cases = None
df_victims = None
subhead_map = {}
police_stations = {}

def load_graph_data():
    global df_accused, df_cases, df_victims, subhead_map, police_stations
    try:
        df_accused = pd.read_csv(accused_path)
        df_cases = pd.read_csv(case_master_path)
        df_victims = pd.read_csv(victim_path)
        
        if os.path.exists(subhead_path):
            sh_df = pd.read_csv(subhead_path)
            for _, r in sh_df.iterrows():
                subhead_map[r['CrimeSubHeadID']] = r['CrimeHeadName']
                
        if os.path.exists(stations_path):
            with open(stations_path, 'r') as f:
                police_stations = json.load(f)
        print("Graph router loaded CSV datasets successfully.")
    except Exception as e:
        print(f"Error loading datasets for graph: {e}")

load_graph_data()


@router.get("/criminals")
def list_top_criminals(limit: int = 50):
    """Returns top criminals with their case counts for search & selection dropdowns."""
    if df_accused is None:
        raise HTTPException(status_code=500, detail="Data not loaded")
        
    counts = df_accused.groupby('AccusedMasterID').agg({
        'AccusedName': 'first',
        'AgeYear': 'first',
        'GenderID': 'first',
        'CaseMasterID': 'count'
    }).rename(columns={'CaseMasterID': 'case_count'}).reset_index()
    
    # Sort by criminals involved in most cases
    sorted_df = counts.sort_values(by='case_count', ascending=False).head(limit)
    
    res = []
    for _, r in sorted_df.iterrows():
        res.append({
            "id": int(r['AccusedMasterID']),
            "name": str(r['AccusedName']),
            "age": int(r['AgeYear']) if pd.notnull(r['AgeYear']) else 30,
            "gender": "Male" if str(r['GenderID']).upper() == 'M' or r['GenderID'] == 1 else "Female",
            "case_count": int(r['case_count'])
        })
    return res


@router.get("/criminal/{id}")
def get_criminal_graph(id: int):
    """Generates real 2nd-degree network graph for a given AccusedMasterID using NetworkX."""
    if df_accused is None or df_cases is None:
        raise HTTPException(status_code=500, detail="Datasets not initialized")

    acc_rows = df_accused[df_accused['AccusedMasterID'] == id]
    if acc_rows.empty:
        # Fallback to first accused if requested ID doesn't exist
        first_id = int(df_accused['AccusedMasterID'].iloc[0])
        acc_rows = df_accused[df_accused['AccusedMasterID'] == first_id]
        id = first_id

    subject_name = str(acc_rows['AccusedName'].iloc[0])
    subject_age = int(acc_rows['AgeYear'].iloc[0]) if pd.notnull(acc_rows['AgeYear'].iloc[0]) else 32
    
    G = nx.Graph()
    
    # Subject Node
    G.add_node(
        f"A_{id}", 
        label=subject_name, 
        type="criminal", 
        role="Subject",
        age=subject_age,
        cases_count=len(acc_rows)
    )

    # Get linked cases
    case_ids = acc_rows['CaseMasterID'].dropna().unique()
    
    for c_id in case_ids[:10]: # Limit to top 10 cases to keep graph readable
        case_row = df_cases[df_cases['CaseMasterID'] == c_id]
        if case_row.empty:
            continue
            
        c_row = case_row.iloc[0]
        crime_sub_id = c_row.get('CrimeMinorHeadID', 1)
        crime_name = subhead_map.get(crime_sub_id, f"Crime #{c_id}")
        ps_id = str(int(c_row['PoliceStationID'])) if pd.notnull(c_row.get('PoliceStationID')) else "Unknown"
        
        station_name = police_stations.get(ps_id, {}).get('name', f"Station #{ps_id}")
        
        node_c_key = f"C_{c_id}"
        G.add_node(
            node_c_key,
            label=f"FIR #{c_row.get('CrimeNo', c_id)}",
            type="incident",
            crime_type=crime_name,
            date=str(c_row.get('CrimeRegisteredDate', '')).split('T')[0],
            facts=str(c_row.get('BriefFacts', ''))[:150] + "..."
        )
        G.add_edge(f"A_{id}", node_c_key, relation="accused_in")
        
        # Add Location Node
        loc_key = f"L_{ps_id}"
        G.add_node(loc_key, label=station_name, type="location")
        G.add_edge(node_c_key, loc_key, relation="jurisdiction")
        
        # Co-accused in this case
        co_acc = df_accused[(df_accused['CaseMasterID'] == c_id) & (df_accused['AccusedMasterID'] != id)]
        for _, co_r in co_acc.head(4).iterrows():
            co_id = int(co_r['AccusedMasterID'])
            co_name = str(co_r['AccusedName'])
            co_key = f"A_{co_id}"
            
            G.add_node(
                co_key, 
                label=co_name, 
                type="criminal", 
                role="Co-Accused",
                age=int(co_r['AgeYear']) if pd.notnull(co_r['AgeYear']) else 28
            )
            G.add_edge(node_c_key, co_key, relation="co_accused_in")
            G.add_edge(f"A_{id}", co_key, relation="associate_of")
            
        # Victims in this case
        if df_victims is not None:
            vic_rows = df_victims[df_victims['CaseMasterID'] == c_id]
            for _, v_r in vic_rows.head(2).iterrows():
                v_id = int(v_r['VictimMasterID'])
                v_name = str(v_r['VictimName'])
                v_key = f"V_{v_id}"
                G.add_node(
                    v_key,
                    label=f"Victim: {v_name}",
                    type="victim",
                    age=int(v_r['AgeYear']) if pd.notnull(v_r['AgeYear']) else 35
                )
                G.add_edge(node_c_key, v_key, relation="victim_in")

    # Format Cytoscape Nodes and Edges
    nodes = []
    for n, data in G.nodes(data=True):
        nodes.append({"id": str(n), **data})
        
    edges = []
    for u, v, data in G.edges(data=True):
        edges.append({"source": str(u), "target": str(v), "relation": data.get("relation", "connected")})

    return {"nodes": nodes, "edges": edges, "subject": {"id": id, "name": subject_name, "age": subject_age}}
