import requests
import datetime
import json
import math


# Calculates distance between coordinates along the Earth's surface

EARTH_RADIUS_KM = 6357

def coords_distance_km(lat_1_deg, lng_1_deg, lat_2_deg, lng_2_deg):

    lng_1, lat_1, lng_2, lat_2 = map(math.radians, [lat_1_deg, lng_1_deg, lat_2_deg, lng_2_deg])

    d_lat = lat_2 - lat_1
    d_lng = lng_2 - lng_1

    temp = (
         math.sin(d_lat / 2) ** 2
       + math.cos(lat_1)
       * math.cos(lat_2)
       * math.sin(d_lng / 2) ** 2
    )

    return EARTH_RADIUS_KM * (2 * math.atan2(math.sqrt(temp), math.sqrt(1 - temp)))



# Google API key
google_api_key = input("Your Google API key: ")

# Vertex count
vertex_count = int(input("Number of vertexes in your path: "))
if vertex_count < 2: print("Need 2 or more vertexes to make a path!"); exit()

# Sample count
sample_count = int(input("Number of samples to take along your path: "))
if sample_count < 1: print("Must take at least one elevation sample!"); exit()


# Prompt for path vertexes

path = []

print(f"\nInput {vertex_count} path vertexes: (format: lat,lng)")

for i in range(0, vertex_count):

    vertex = input(f"  - Vertex {i + 1}: ")
    vertex = vertex.replace(" ", "")

    path.append(vertex)


# Print loaded path

path_string = path[0]

for vertex in path[1:]:
    path_string += f" -> {vertex}"

print(f"\nLoaded path: {path_string}")

# Confirm
if input(f"Request {sample_count} elevation samples from Google Elevation API? (beware of pricing tiers) [Y/N] ") != "Y":
    exit()


# Compose path URL parameter from previous string
path_url_parameter = path_string.replace(" -> ", "|")

# Compose HTTP request URL
url = f"https://maps.googleapis.com/maps/api/elevation/json?path={path_url_parameter}&samples={sample_count}&key={google_api_key}"

# Call Google Elevation API
response = requests.get(url)
response.raise_for_status()

# Parse JSON
response = response.json()

# Check response status
elevation_status = response["status"]
if elevation_status != "OK":
    print(f"WARNING: API returned ElevationStatus \"{elevation_status}\" instead of \"OK\", carefully check your results!")

# Save original results to file
file = open(f"elevation_responses_{datetime.datetime.now().isoformat()}.json", "w")
file.write(json.dumps(response["results"]))


