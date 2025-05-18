import pandas as pd
import geopandas as gpd
import requests
import math

from PIL import Image, ImageDraw

poi_gdf = gpd.read_file("POIs\POI_4815075_1.geojson")
roads_gdf = gpd.read_file("STREETS_NAV\SREETS_NAV_4815075.geojson")

poi_gdf = poi_gdf.to_crs(epsg=4326)
roads_gdf = roads_gdf.to_crs(epsg=4326)

item = 18

longitude, latitude = poi_gdf.geometry.iloc[item].x, poi_gdf.geometry.iloc[item].y

link_id = poi_gdf.iloc[item]["LINK_ID"] if "LINK_ID" in poi_gdf.columns else poi_gdf.iloc[item]["link_id"]

# Buscar la geometría correspondiente en STREET
line = roads_gdf[roads_gdf["link_id"] == link_id].geometry.values[0]


start_point = line.coords[0]       # (lon, lat)
end_point = line.coords[-1]        # (lon, lat)

all_points = list(line.coords)

def lat_lon_to_tile(lat, lon, zoom):
    """
    Convert latitude and longitude to tile indices (x, y) at a given zoom level.
    
    :param lat: Latitude in degrees
    :param lon: Longitude in degrees
    :param zoom: Zoom level (0-19)
    :return: Tuple (x, y) representing the tile indices
    """
    # Convert latitude and longitude to radians
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)
    
    # Calculate n (number of tiles at the given zoom level)
    n = 2.0 ** zoom
    
    # Calculate x and y tile indices
    x = int((lon_rad - (-math.pi)) / (2 * math.pi) * n)
    y = int((1 - math.log(math.tan(lat_rad) + 1 / math.cos(lat_rad)) / math.pi) / 2 * n)
    
    return (x, y)

def tile_coords_to_lat_lon(x, y, zoom):
    n = 2.0 ** zoom
    lon_deg = x / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1-2 * y/n)))
    lat_def = math.degrees(lat_rad)
    return (lat_def, lon_deg)

def get_tile_bounds(x, y, zoom):
    lat1, lon1 = tile_coords_to_lat_lon(x,y,zoom)
    lat2, lon2 = tile_coords_to_lat_lon(x+1, y, zoom)
    lat3, lon3 = tile_coords_to_lat_lon(x+1,y+1,zoom)
    lat4, lon4 = tile_coords_to_lat_lon(x,y+1,zoom)
    return (lat1, lon1), (lat2, lon2), (lat3, lon3), (lat4, lon4)

def create_wkt_polygon(bounds):
    (lat1, lon1), (lat2, lon2), (lat3, lon3), (lat4, lon4) = bounds
    wkt = {
    'top_left': (lat1, lon1),
    'top_right': (lat2, lon2),
    'bottom_left': (lat3, lon3),
    'bottom_right': (lat4, lon4),
}
    return wkt



def get_satellite_tile(lat,lon,zoom,tile_format,api_key):

    x,y =lat_lon_to_tile(lat, lon, zoom)


    # Construct the URL for the map tile API
    url = f'https://maps.hereapi.com/v3/base/mc/{zoom}/{x}/{y}/{tile_format}&style=satellite.day&size={tile_size}?apiKey={api_key}'

    # Make the request
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Save the tile to a file
        with open(f'satellite_tile.{tile_format}', 'wb') as file:
            file.write(response.content)
        print('Tile saved successfully.')
    else:
        print(f'Failed to retrieve tile. Status code: {response.status_code}')

    bounds = get_tile_bounds(x,y, zoom)
    wkt_polygon = create_wkt_polygon(bounds)
    return wkt_polygon

##########################################################
### Image Markers
##########################################################

def plot_marker_on_image(image_path, corners, marker_lat_lon, output_path,color):
    """
    :param image_path: Path to the satellite image.
    :param corners: A dictionary with 'top_left', 'top_right', 'bottom_left', 'bottom_right' lat-lon pairs.
    :param marker_lat_lon: Tuple of (latitude, longitude) for the marker.
    :param output_path: Path to save the output image.
    """
    # Load the image
    img = Image.open(image_path)
    width, height = img.size
    
    # Extract corner coordinates
    tl_lat, tl_lon = corners['top_left']  # Top-left corner
    tr_lat, tr_lon = corners['top_right']  # Top-right corner
    bl_lat, bl_lon = corners['bottom_left']  # Bottom-left corner
    br_lat, br_lon = corners['bottom_right']  # Bottom-right corner
    
    marker_lat, marker_lon = marker_lat_lon
    
    # Calculate longitude interpolation (x-coordinate)
    # Assuming linear variation in longitude along the top edge
    lon_span_top = tr_lon - tl_lon
    lon_frac_top = (marker_lon - tl_lon) / lon_span_top if lon_span_top != 0 else 0
    x_pixel = lon_frac_top * width
    
    # Calculate latitude interpolation (y-coordinate)
    # Assuming linear variation in latitude along the left edge
    lat_span_left = bl_lat - tl_lat
    lat_frac_left = (marker_lat - tl_lat) / lat_span_left if lat_span_left != 0 else 0
    y_pixel = lat_frac_left * height
    
    
    draw = ImageDraw.Draw(img)
    marker_radius = 8
    draw.ellipse(
        [(x_pixel - marker_radius, y_pixel - marker_radius),
         (x_pixel + marker_radius, y_pixel + marker_radius)],
        fill=color,
        outline=color
    )
    
    # Save the result
    img.save(output_path)
    print(f"Image saved to {output_path}")

def plot_points_and_line(
    image_path, 
    corners, 
    point1_lat_lon, 
    point2_lat_lon, 
    output_path,
    marker_radius=5,
    line_width=3
):
    
    img = Image.open(image_path)
    draw = ImageDraw.Draw(img)
    width, height = img.size

    def lat_lon_to_pixel(lon, lat): 
        # Longitude interpolation (x-coordinate)
        lon_span = corners['top_right'][1] - corners['top_left'][1]
        x_frac = (lon - corners['top_left'][1]) / lon_span if lon_span != 0 else 0
        x_pixel = x_frac * width

        # Latitude interpolation (y-coordinate)
        lat_span = corners['bottom_left'][0] - corners['top_left'][0]
        y_frac = (lat - corners['top_left'][0]) / lat_span if lat_span != 0 else 0
        y_pixel = y_frac * height

        return (x_pixel, y_pixel)
    
    x1, y1 = lat_lon_to_pixel(*point1_lat_lon)
    x2, y2 = lat_lon_to_pixel(*point2_lat_lon)
    
    draw.line([(x1, y1), (x2, y2)], fill="yellow", width=line_width)

    for (x, y) in [(x1, y1), (x2, y2)]:
        draw.ellipse(
            [(x - marker_radius, y - marker_radius),
             (x + marker_radius, y + marker_radius)],
            fill="yellow",
            outline="yellow"
        )

    img.save(output_path)
    print(f"Image saved to {output_path}")

##########################################################
### EXECUTION
##########################################################

# POI: { "type": "Feature", "properties": { "Unnamed: 0": 151721, "LINK_ID": 939199332, "POI_ID": 1178940592, "SEQ_NUM": 1, "FAC_TYPE": 7538, "POI_NAME": "NIETO", "POI_LANGCD": "SPA", "POI_NMTYPE": "B", "POI_ST_NUM": null, "ST_NUM_FUL": null, "ST_NFUL_LC": null, "ST_NAME": "AVENIDA SOLIDARIDAD LAS TORRES", "ST_LANGCD": "SPA", "POI_ST_SD": "L", "ACC_TYPE": null, "PH_NUMBER": null, "CHAIN_ID": 0, "NAT_IMPORT": "N", "PRIVATE": "N", "IN_VICIN": "N", "NUM_PARENT": 0, "NUM_CHILD": 0, "PERCFRREF": 84.0, "VANCITY_ID": 0, "ACT_ADDR": null, "ACT_LANGCD": null, "ACT_ST_NAM": null, "ACT_ST_NUM": null, "ACT_ADMIN": null, "ACT_POSTAL": null, "AIRPT_TYPE": null, "ENTR_TYPE": null, "REST_TYPE": null, "FOOD_TYPE": null, "ALT_FOOD": null, "REG_FOOD": null, "RSTR_TYPE": null, "OPEN_24": null, "DIESEL": null, "BLD_TYPE": null, "link_id": 939199332 }, "geometry": { "type": "Point", "coordinates": [ -99.64272, 19.27055 ] } },

# STREET: { "type": "Feature", "properties": { "AR_AUTO": "Y", "AR_BUS": "Y", "AR_CARPOOL": "Y", "AR_DELIV": "Y", "AR_EMERVEH": "Y", "AR_MOTOR": "Y", "AR_PEDEST": "Y", "AR_TAXIS": "Y", "AR_TRAFF": "Y", "AR_TRUCKS": "Y", "BRIDGE": "N", "CONTRACC": "N", "COVERIND": "N0", "DIR_TRAVEL": "T", "DIVIDER": "N", "FERRY_TYPE": "H", "FROM_LANES": 0, "FRONTAGE": "Y", "FR_SPD_LIM": 0, "FUNC_CLASS": "4", "INDESCRIB": "N", "INTERINTER": "N", "LANE_CAT": "2", "link_id": 939199332, "LOW_MBLTY": "3", "MANOEUVRE": "N", "MULTIDIGIT": "N", "PAVED": "Y", "POIACCESS": "N", "PRIORITYRD": "N", "PRIVATE": "N", "PUB_ACCESS": "Y", "RAMP": "N", "ROUNDABOUT": "N", "SPEED_CAT": "6", "TOLLWAY": "N", "TO_LANES": 0, "TO_SPD_LIM": 40, "TUNNEL": "N", "UNDEFTRAFF": "N", "URBAN": "Y" }, "geometry": { "type": "LineString", "coordinates": [ [ -99.64464, 19.27013 ], [ -99.64272, 19.27055 ] ] } },

# Define the parameters for the tile request
api_key = '<API KEY>'
#latitude = 19.27055
#longitude = -99.64272
zoom_level = 16  # Zoom level
tile_size = 512  # Tile size in pixels
tile_format = 'png'  # Tile format
print(f"Latitud: {latitude}, Longitud: {longitude}")

# Execute request and save tile
corners = get_satellite_tile(latitude,longitude,zoom_level,tile_format,api_key)
print(corners)

# Street Marker

#points = [ [ 19.27013, -99.64464 ], [19.27055, -99.64272 ] ]
#points = [[start_point[1], start_point[0]], [end_point[1], end_point[0]]]
pointA = all_points[0]
pointB = all_points[1]

latref = pointA[1]
lonref = pointA[0]

while(len(all_points)>=2):
    print("Puntos extraídos:", all_points)

    plot_points_and_line(
        "satellite_tile.png",
        corners,
        pointA,
        pointB,
        "satellite_tile.png"
    )
    
    all_points.pop(0)
    if(len(all_points)!=1):
        pointA = all_points[0]
        pointB = all_points[1]


plot_marker_on_image(
    'satellite_tile.png',
    corners,
    (latitude,longitude),
    'satellite_tile.png',
    'red'
)
plot_marker_on_image(
    'satellite_tile.png',
    corners,
    (latref,lonref),
    'satellite_tile.png',
    'white'
)