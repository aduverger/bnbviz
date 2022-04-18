import streamlit as st
from streamlit_folium import folium_static
import folium
import geopandas as gpd
import math
import requests
from geopy.geocoders import Nominatim
from pyproj import Transformer

st.markdown("# BDNB Viz 🗺")

address = st.text_input("Adresse recherchée", "11 rue de Charonne, 75011 Paris, France")
radius = st.slider(
    "Sélectionnez un rayon (en km) autour de l'adresse recherchée. Restez à 1km pour de meilleures performances :)",
    1,
    3,
    1,
)
# Get bbox coordinates
geolocator = Nominatim(user_agent="bnbviz")
location = geolocator.geocode(address)
x, y = location.latitude, location.longitude
xmin = x - radius / (2 * 110.574)
xmax = x + radius / (2 * 110.574)
ymin = y - radius / (2 * 111.320 * math.cos(math.pi * x / 180))
ymax = y + radius / (2 * 111.320 * math.cos(math.pi * x / 180))
transformer = Transformer.from_crs("epsg:4326", "epsg:2154")
xmin, ymin = transformer.transform(xmin, ymin)
xmax, ymax = transformer.transform(xmax, ymax)

url = "https://bdnb-image-fzyx4l7upa-ew.a.run.app/"
url += f"getbbox?xmin={xmin}&xmax={xmax}&ymin={ymin}&ymax={ymax}"
data = requests.get(url).json()
gdf = gpd.GeoDataFrame.from_features(data["features"])
gdf = gdf.set_crs(epsg=2154)

option = st.selectbox(
    "Quel critère souhaitez-vous afficher sur la carte ?",
    ("Etiquette énergétique", "Etiquette carbone"),
)
if option == "Etiquette énergétique":
    feature = "Etiquette énergétique (DPE)"
else:
    feature = "Etiquette carbone (DPE)"

gdf.fillna(value="N.C.", inplace=True)
gdf["Etiquette énergétique (DPE)"].replace(to_replace="N", value="N.C.", inplace=True)
gdf["Etiquette carbone (DPE)"].replace(to_replace="N", value="N.C.", inplace=True)


color = [
    "#309C6C",
    "#5FB14E",
    "#80BD73",
    "#F2E600",
    "#EAB400",
    "#E3812A",
    "#CE1E15",
    "#C3C3C3",
]
m = gdf.explore(
    feature,
    cmap=color,
    tiles="CartoDB positron",
    zoom_start=18,
    location=(x, y),
    legend=True,
)
folium.Marker(
    location=[x, y], icon=folium.Icon(color="darkblue", icon="map-pin", prefix="fa")
).add_to(m)
folium_static(m)
