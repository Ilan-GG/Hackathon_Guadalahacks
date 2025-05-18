
import json
import csv
from collections import defaultdict

with open('POI_4815075.geojson', 'r', encoding='utf-8') as f:
    data = json.load(f)

seen = defaultdict(list)

total_features = len(data['features'])
print(f"Total de features: {total_features}")

for feature in data['features']:
    props = feature['properties']
    coords = tuple(feature['geometry']['coordinates'])  # (lon, lat)
    key = (props['POI_ID'], coords)
    seen[key].append(feature)

duplicates = [group for group in seen.values() if len(group) > 1]
print(f"Total de grupos duplicados encontrados: {len(duplicates)}")

if duplicates:
    with open('repeatedData_POI_4815075.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['POI_ID', 'Longitude', 'Latitude', 'SEQ_NUM', 'POI_NAME', 'LINK_ID']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for group in duplicates:
            for feature in group:
                props = feature['properties']
                lon, lat = feature['geometry']['coordinates']
                writer.writerow({
                    'POI_ID': props['POI_ID'],
                    'Longitude': lon,
                    'Latitude': lat,
                    'SEQ_NUM': props['SEQ_NUM'],
                    'POI_NAME': props.get('POI_NAME', ''),
                    'LINK_ID': props.get('LINK_ID', '')
                })

    print("Repetidos guardados en repeatedData.csv")
else:
    print("No se encontraron duplicados.")
