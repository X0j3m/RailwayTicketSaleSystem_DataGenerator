from geopy.distance import geodesic
from common.models import *
from common.json_handler import *

def calculate_distance(connection: ConnectionModel) -> int:
    start_station_code = connection.source_id
    end_station_code = connection.target_id

    start_station = list(filter(lambda s: s.id == start_station_code, stations))
    end_station = list(filter(lambda s: s.id == end_station_code, stations))

    start_station_coords = (start_station[0].latitude, start_station[0].longitude)
    end_station_coords = (end_station[0].latitude, end_station[0].longitude)

    dist = geodesic(start_station_coords, end_station_coords).km
    return round(dist)
stations_dict = open_json_file("train_stations")
stations = [StationModel(**item) for item in stations_dict]