import streamlit as st
from streamlit_folium import st_folium
import folium

# UI input
st.title("CVRP Route Visualizer")
vehicle_count = st.slider("Number of Vehicles", 1, 10, 2)

# Sample coordinates
locations = {
    "Depot": (52.52, 13.405),
    "Customer1": (52.54, 13.40),
    "Customer2": (52.50, 13.39),
    "Customer3": (52.51, 13.42),
}

# Your CVRP solver would go here and return routes
routes = [[0, 1, 2, 0], [0, 3, 0]]  # Example route indices

# Create map
m = folium.Map(location=locations["Depot"], zoom_start=13)
coords = list(locations.values())
names = list(locations.keys())

# Plot points
for name, (lat, lon) in locations.items():
    folium.Marker([lat, lon], popup=name).add_to(m)

# Plot routes
colors = ['red', 'blue', 'green', 'purple']
for idx, route in enumerate(routes):
    points = [coords[i] for i in route]
    folium.PolyLine(points, color=colors[idx % len(colors)], weight=5).add_to(m)

st_folium(m)