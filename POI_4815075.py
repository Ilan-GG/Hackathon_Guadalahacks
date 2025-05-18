import pandas as pd
import geopandas as gpd
from shapely.geometry import LineString

# Load POI data and road geometry
poi_df = pd.read_csv("POI_4815075.csv")
roads_gdf = gpd.read_file("../STREETS_NAV/SREETS_NAV_4815075.geojson")
print(roads_gdf.columns)
print(poi_df.columns)
# Merge to get road geometries
merged = poi_df.merge(roads_gdf[['link_id', 'geometry']], left_on='LINK_ID', right_on='link_id')

# Interpolate point along each road
def get_point(row):
    line: LineString = row['geometry']
    return line.interpolate((row['PERCFRREF']/100) * line.length)

merged['geometry'] = merged.apply(get_point, axis=1)

# Convert to GeoDataFrame and export
poi_gdf = gpd.GeoDataFrame(merged, geometry='geometry', crs=roads_gdf.crs)
poi_gdf.to_file("POI_4815075_1.geojson", driver="GeoJSON")
