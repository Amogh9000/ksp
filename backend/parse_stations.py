import re
import pandas as pd

with open('pdf_text.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

stations = []
for line in lines:
    line = line.strip()
    # Match lines starting with PI and ending before numbers or email
    if line.startswith('PI '):
        # Remove 'PI ' prefix
        name = line[3:].strip()
        # Remove 'TR. ' if it's traffic
        if name.startswith('TR.'):
            name = name[3:].strip()
        elif name.startswith('TR '):
            name = name[3:].strip()
            
        # Try to find the end of the name. It usually ends before 'PS', '080-', or numbers
        # Let's use a regex to extract just the text part before any numbers
        match = re.search(r'^([A-Za-z\.\s]+)(?:\s+PS|\s+080-|\s+\d)', name, re.IGNORECASE)
        if match:
            clean_name = match.group(1).strip()
            if clean_name and clean_name not in stations and "SECURITY" not in clean_name and clean_name != "PLANNING" and clean_name != "F&M" and clean_name != "W&N" and clean_name != "OCW" and clean_name != "SE" and clean_name != "H&B":
                stations.append(clean_name)
        elif "PS" in name:
            clean_name = name.split("PS")[0].strip()
            if clean_name and clean_name not in stations and "SECURITY" not in clean_name:
                stations.append(clean_name)

# Now, we need to save this to police_stations.csv in the catalyst_csv_bundle
csv_path = r'catalyst_csv_bundle\police_stations.csv'
df = pd.DataFrame({
    'Sl': range(1, len(stations) + 1),
    'Station Code': '',
    'Station': stations,
    'Unit': 'Bangalore City',
    'DCP': '',
    'ACP': ''
})
df.to_csv(csv_path, index=False)

print(f"Extracted {len(stations)} stations to {csv_path}")
