import os
import re
import json
import pandas as pd

text_path = r"c:\Users\Admin\OneDrive\Desktop\KSP\backend\pdf_text.txt"
json_path = r"c:\Users\Admin\OneDrive\Desktop\KSP\backend\geocoded_stations.json"

if not os.path.exists(text_path):
    print("pdf_text.txt not found!")
    exit(1)

with open(text_path, 'r', encoding='utf-8') as f:
    text = f.read()

lines = text.split('\n')

current_division = "CENTRAL DIVISION"
stations_meta = {}

for line in lines:
    line_str = line.strip()
    if not line_str:
        continue
        
    # Check for division headers
    if "DIVISION" in line_str and not line_str.startswith("PI ") and not line_str.startswith("ACP "):
        current_division = line_str
        continue
        
    if line_str.startswith("PI ") or " PS" in line_str or "CEN PS" in line_str:
        # Determine Station Category
        stype = "Law & Order"
        if "TR." in line_str or "TRAFFIC" in line_str or "TRAFFIC" in current_division:
            stype = "Traffic"
        elif "CEN PS" in line_str or "CYBER" in line_str:
            stype = "CEN (Cyber/Narcotics)"
        elif "WOMEN" in line_str:
            stype = "Women PS"
        elif "CCB" in line_str or "CRIME" in current_division:
            stype = "CCB"
            
        # Extract Mobile Number (starts with 94808 or 95135)
        mob_match = re.search(r'(94808\d{5}|95135\d{5}|9448\d{6})', line_str)
        mobile = mob_match.group(1) if mob_match else "080-22942222"
        
        # Extract Email
        email_match = re.search(r'([a-zA-Z0-9_\.]+(?:\[at\]|@)[a-zA-Z0-9\.]+\.in)', line_str)
        email = email_match.group(1).replace('[at]', '@') if email_match else "controlroom@ksp.gov.in"
        
        # Clean Station Name
        clean_name = line_str
        clean_name = re.sub(r'^PI\s+', '', clean_name)
        clean_name = re.sub(r'^TR\.\s*', '', clean_name)
        clean_name = re.sub(r'080-\d+.*$', '', clean_name)
        clean_name = re.sub(r'94808.*$', '', clean_name)
        clean_name = clean_name.strip()
        
        if clean_name and len(clean_name) > 3 and "SECURITY" not in clean_name and "ADMIN" not in clean_name:
            stations_meta[clean_name] = {
                "division": current_division,
                "type": stype,
                "mobile": mobile,
                "email": email
            }

print(f"Extracted metadata for {len(stations_meta)} police stations.")

# Merge enriched metadata into existing geocoded_stations.json
if os.path.exists(json_path):
    with open(json_path, 'r') as f:
        geocoded = json.load(f)
        
    enriched_count = 0
    for sid, sdata in geocoded.items():
        sname = sdata.get('name', '')
        # Try to match metadata
        matched = False
        for mname, meta in stations_meta.items():
            first_word = mname.split(' ')[0].lower()
            if first_word in sname.lower() or sname.lower().startswith(first_word):
                sdata['division'] = meta['division']
                sdata['type'] = meta['type']
                sdata['mobile'] = meta['mobile']
                sdata['email'] = meta['email']
                matched = True
                enriched_count += 1
                break
                
        if not matched:
            sdata['division'] = "BENGALURU CITY POLICE"
            sdata['type'] = "Law & Order" if "Traffic" not in sname else "Traffic"
            sdata['mobile'] = "9480801000"
            sdata['email'] = "bcp.control@ksp.gov.in"
            
    with open(json_path, 'w') as f:
        json.dump(geocoded, f, indent=4)
        
    print(f"Enriched {enriched_count}/{len(geocoded)} geocoded stations with division, category, phone, and email metadata!")
