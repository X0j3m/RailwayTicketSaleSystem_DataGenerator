import uuid

from distance_couter import *
from models import *
from json_handler import *

stations_dict = open_json_file("train_stations")
stations = [StationModel(**item) for item in stations_dict]
stations_by_id = {s.id: s for s in stations if s.id is not None}

def fill_connections_data():
    connections_dict = open_json_file("train_stations_connections")
    connections = [ConnectionModel(**item) for item in connections_dict]

    for connection in connections:
        distance = calculate_distance(connection)

        start_station = stations_by_id.get(connection.source_id)
        end_station = stations_by_id.get(connection.target_id)

        connection.id = str(uuid.uuid4())
        connection.source_name = start_station.name
        connection.target_name = end_station.name
        connection.distance = distance

    connections_dict = [obj.model_dump() for obj in connections]
    save_json_file("train_stations_connections", connections_dict)

    print()
    print(stations)
    print(connections)
