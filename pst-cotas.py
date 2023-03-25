import requests
import datetime
import json
import math
import haversine


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

# Extract elevation results
results = response["results"]

# Save original results to file
file = open(f"original_elevation_samples_{datetime.datetime.now().isoformat().replace(":", "-")}.json", "w")
file.write(json.dumps(results))

# Convert to target format (distance, elevation)
elevation_samples = []

# Add first point
elevation_samples.append((0, results[0]["elevation"]))

# Calculate distances

for i, result in enumerate(results[1:], 1):

    previous_location = results[i - 1]["location"]
    previous_lat = previous_location["lat"]
    previous_lng = previous_location["lng"]
    
    previous_distance = elevation_samples[i - 1][0]

    location = result["location"]
    lat = location["lat"]
    lng = location["lng"]

    distance = previous_distance + haversine.Haversine((previous_lat, previous_lng), (lat, lng)).km
    elevation = result["elevation"]

    elevation_samples.append((distance, elevation))

# Write out results

file = open(f"elevation_samples_{datetime.datetime.now().isoformat().replace(":", "-")}.txt", "w")

for sample in elevation_samples:
    file.write(f"{sample[0]} {sample[1]}\n")

file.close()