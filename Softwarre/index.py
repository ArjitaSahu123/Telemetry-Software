import folium
from data import trajectory, timestamps

# initialize a map with center and zoom
mapObj = folium.Map(location=trajectory[0],
                     zoom_start=9)

shapesLayer = folium.FeatureGroup(name="trajectory and markers").add_to(mapObj)

for coord, timestamp in zip(trajectory, timestamps):
    folium.CircleMarker(
        location=coord,
        radius=5,  # Adjust this value to control the circle size
        color="red",  # Outline color of the circle
        fill=True,
        fill_color="red",  # Fill color
        fill_opacity=0.7,
        tooltip=f"Lat: {coord[0]}, Lon: {coord[1]}<br>Timestamp: {timestamp}"
    ).add_to(mapObj)

folium.PolyLine(trajectory, color="green", weight=4).add_to(shapesLayer)

folium.LayerControl().add_to(mapObj)

# save the map as html file
mapObj.save('output.html')