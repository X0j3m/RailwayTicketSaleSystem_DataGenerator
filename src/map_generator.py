import urllib.request
import socket

import geopandas as gpd
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
from shapely.geometry import Point
from json_handler import *
from models import *
from stations.city_locator import *
from time import sleep
import uuid

RES_PATH = "../res"
OUTPUT_PDF_FILENAME = "mapa_polski_wojewodztwa.pdf"
OUTPUT_PDF_FILE_PATH = os.path.join(RES_PATH, OUTPUT_PDF_FILENAME)

LOCAL_GEOJSON_PATH = os.path.join(RES_PATH, "wojewodztwa-min.geojson")
# URL = "https://raw.githubusercontent.com/ppatrzyk/polska-geojson/master/wojewodztwa/wojewodztwa-min.geojson"
URL = "https://raw.githubusercontent.com/ppatrzyk/polska-geojson/master/wojewodztwa/wojewodztwa-max.geojson"

def generate_map():
    os.makedirs(RES_PATH, exist_ok=True)

    if not os.path.exists(LOCAL_GEOJSON_PATH):
        print("Downloading geojson...")
        try:
            socket.setdefaulttimeout(10)
            urllib.request.urlretrieve(URL, LOCAL_GEOJSON_PATH)
        except Exception as e:
            print(f"{e}")
            os._exit(1)

    stations_dict = open_json_file("train_stations")
    stations = [StationModel(**item) for item in stations_dict]

    connections_dict = open_json_file("train_stations_connections")
    connections = [ConnectionModel(**item) for item in connections_dict]

    n_of_stations = len(stations)

    for i, station in enumerate(stations):
        if station.latitude is None or station.longitude is None:
            lat, lon = get_station_location(station)
            station.latitude = lat
            station.longitude = lon
            sleep(1)
        if station.id is None:
            station.id = str(uuid.uuid4())
        progress = round((i + 1) / n_of_stations * 100)
        print(f"Progress {progress}%")

    stations_dict = [obj.model_dump() for obj in stations]
    save_json_file("train_stations", stations_dict)

    poland_provinces = gpd.read_file(LOCAL_GEOJSON_PATH)

    poland_provinces = poland_provinces.to_crs(epsg=2180)

    station_geometries = [Point(s.longitude, s.latitude) for s in stations]
    stations_gdf = gpd.GeoDataFrame(
        geometry=station_geometries,
        crs="EPSG:4326"
    )
    stations_gdf['station_id'] = [s.id for s in stations]
    stations_gdf = stations_gdf.set_index('station_id')

    stations_gdf = stations_gdf.to_crs(epsg=2180)

    fig, ax = plt.subplots(figsize=(10, 10))

    poland_provinces.plot(ax=ax, facecolor='white', edgecolor='#8a8a8a', linewidth=0.5)
    stations_gdf.plot(ax=ax, color='#b5b5b5', markersize=10, zorder=4)

    for idx, row in stations_gdf.iterrows():
        station = next((s for s in stations if str(s.id) == str(idx)), None)
        station_name = station.city

        x = row['geometry'].x
        y = row['geometry'].y

        bbox_props = dict(
            boxstyle="round,pad=0.3",
            facecolor="#119448",
            linewidth=0.5,
        )

        ax.text(
            x + 4000,
            y + 4000,
            station_name,
            fontsize=5,
            color='white',
            zorder=5,
            bbox=bbox_props
        )

    for connection in connections:
        if connection.source_id not in stations_gdf.index or connection.target_id not in stations_gdf.index:
            print(f"Ominięto połączenie: Brak stacji {connection.source_id} lub {connection.target_id} na mapie.")
            continue

        geom_a = stations_gdf.loc[connection.source_id].geometry
        geom_b = stations_gdf.loc[connection.target_id].geometry

        ax.plot(
            [geom_a.x, geom_b.x],
            [geom_a.y, geom_b.y],
            color='red',
            linewidth=0.5,
            linestyle='-',
            zorder=3
        )

    ax.set_axis_off()
    plt.tight_layout()

    plt.savefig(OUTPUT_PDF_FILE_PATH, format='pdf', dpi=300, bbox_inches='tight')
    plt.close(fig)

    print(f"\n\nMap saved in: {OUTPUT_PDF_FILE_PATH}")

    os._exit(0)


if __name__ == "__main__":
    generate_map()
