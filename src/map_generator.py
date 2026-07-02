import urllib.request
import socket
import uuid

import geopandas as gpd
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
from shapely.geometry import Point
from common.json_handler import *
from common.models import *
from stations.city_locator import *

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
        lat, lon = get_station_location(station)
        station.latitude = lat
        station.longitude = lon
        station.id = str(uuid.uuid4())
        sleep(1)
        progress = round((i + 1) / n_of_stations*100)
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
            x + 2000,
            y + 2000,
            station_name,
            fontsize=5,
            color='white',
            # alpha=0.8,
            zorder=5,
            bbox=bbox_props
        )

    for connection in connections:
        geom_a = stations_gdf.loc[connection.source_id].geometry
        geom_b = stations_gdf.loc[connection.target_id].geometry

        ax.plot(
            [geom_a.x, geom_b.x],
            [geom_a.y, geom_b.y],
            # color='#1200bb',
            color='red',
            linewidth=0.5,
            linestyle='-',
            zorder=3
        )

        mid_x = (geom_a.x + geom_b.x) / 2
        mid_y = (geom_a.y + geom_b.y) / 2

        # dy = geom_b.y - geom_a.y
        # dx = geom_b.x - geom_a.x
        # angle_rad = np.arctan2(dy, dx)
        # angle_deg = np.degrees(angle_rad)
        #
        # if angle_deg > 90:
        #     angle_deg -= 180
        # elif angle_deg < -90:
        #     angle_deg += 180

        line_bbox = dict(
            boxstyle="square,pad=0.1",
            facecolor="white",
            edgecolor="none",
            alpha=0.85
        )

        # text_label = f'"num_id": {connection.num_id}'
        text_label = ""

        ax.text(
            mid_x,
            mid_y,
            text_label,
            fontsize=4,
            color='#555555',
            ha='center',
            va='center',
            zorder=4,
            bbox=line_bbox
        )

    ax.set_axis_off()
    plt.tight_layout()

    plt.savefig(OUTPUT_PDF_FILE_PATH, format='pdf', dpi=300, bbox_inches='tight')
    plt.close(fig)

    print(f"\n\nMap saved in: {OUTPUT_PDF_FILE_PATH}")

    os._exit(0)


if __name__ == "__main__":
    generate_map()
