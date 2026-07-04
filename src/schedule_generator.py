import uuid

from networkx.algorithms.operators.binary import difference

from json_handler import *
from models import *
import random
from datetime import time, datetime, timedelta

RES_PATH = "../res"
DAY_SECONDS = 24 * 60 * 60

stations_dict = open_json_file("train_stations", RES_PATH)
stations = [StationModel(**item) for item in stations_dict]

routes_dict = open_json_file("train_routes", RES_PATH)
routes = [RouteModel(**item) for item in routes_dict]

connections_dict = open_json_file("train_stations_connections", RES_PATH)
connections = [ConnectionModel(**item) for item in connections_dict]

compositions_dict = open_json_file("compositions", RES_PATH)
compositions = [TrainCompositionModel(**item) for item in compositions_dict]

trains_dict = open_json_file("trains", RES_PATH)
trains = [TrainModel(**item) for item in trains_dict]


def generate_time():
    hour = random.randint(0, 23)
    minute = random.randint(0, 59)
    return time(hour, minute, 0)


def get_distance(s1_id: str, s2_id: str):
    connction = list(filter(lambda conn:
                            (conn.source_id == s1_id and conn.target_id == s2_id)
                            or
                            (conn.source_id == s2_id and conn.target_id == s1_id),
                            connections))[0]
    return connction.distance


def calculate_waiting_time(stop1_id, stop2_id, stops):
    stop1 = next(item for item in stops if item["id"] == stop1_id)
    stop2 = next(item for item in stops if item["id"] == stop2_id)

    time1 = datetime.strptime(stop1['start_station_time'], "%H:%M:%S")
    time2 = datetime.strptime(stop2['start_station_time'], "%H:%M:%S")

    try:
        time1 += timedelta(minutes=stop1['arrival_time_minutes'])
    except TypeError:
        time1 += timedelta(minutes=stop1['departure_time_minutes'])
    try:
        time2 += timedelta(minutes=stop2['departure_time_minutes'])
    except TypeError:
        return -1

    if time2 < time1:
        time2 += timedelta(days=1)

    diff = time2 - time1
    diff_in_minutes = int(diff.total_seconds() / 60)

    return diff_in_minutes


def generate_transfers(stops):
    transfers = []
    stops_stations = {}
    for stop in stops:
        stop_station = stop['station_id']
        if stop_station not in stops_stations:
            stops_stations[stop_station] = []
        stops_stations[stop_station].append(stop['id'])

    print(f"STATIONS: {len(stops_stations)}")
    iterator = 1
    for station in stops_stations:
        print(f"{iterator}. STATION_STOPS: {len(stops_stations[station])}")
        iterator += 1
        for i in range(len(stops_stations[station])):
            for j in range(len(stops_stations[station])):
                if i != j:
                    from_stop_id = stops_stations[station][i]
                    to_stop_id = stops_stations[station][j]
                    waiting_time = calculate_waiting_time(from_stop_id, to_stop_id, stops)
                    if 0 <= waiting_time <= 6 * 60:
                        transfer = TransferRelationModel(
                            id=str(uuid.uuid4()),
                            from_stop_id=from_stop_id,
                            to_stop_id=to_stop_id,
                            waiting_time=waiting_time
                        )
                        transfers.append(transfer.__dict__)

    return transfers


def generate_schedule():
    stops = []
    stops_connections = []
    for route in routes:
        train_composition = compositions.pop(random.randrange(len(compositions)))
        train = list(filter(lambda item: item.id == train_composition.train_id, trains))[0]
        train_velocity = train.velocity
        start_time = generate_time()
        date = datetime(2000, 1, 1)
        date += timedelta(hours=start_time.hour, minutes=start_time.minute, seconds=start_time.second)
        trip_time = 0
        arrival_time = None
        departure_time = None
        prev_stop_id = None
        prev_departure_time = 0
        for i, station_id in enumerate(route.route):
            stop_id = str(uuid.uuid4())
            stop_minutes = random.randint(1, 10)
            if station_id == route.start_station_code:
                arrival_time = None
                departure_time = trip_time
                prev_departure_time = departure_time
                next_station_id = route.route[i + 1]
                distance_to_next_station = get_distance(station_id, next_station_id)
                trip_time += round((distance_to_next_station / train_velocity) * 60)
            else:
                if station_id != route.end_station_code:
                    arrival_time = trip_time
                    trip_time += stop_minutes
                    prev_departure_time = departure_time
                    departure_time = trip_time
                    next_station_id = route.route[i + 1]
                    distance_to_next_station = get_distance(station_id, next_station_id)
                    trip_time += round((distance_to_next_station / train_velocity) * 60)
                if station_id == route.end_station_code:
                    arrival_time = trip_time
                    prev_departure_time = departure_time
                    departure_time = None

                leads_to_relation = LeadsToRelationModel(
                    id=str(uuid.uuid4()),
                    from_stop_id=prev_stop_id,
                    to_stop_id=stop_id,
                    duration=arrival_time - prev_departure_time,
                )
                stops_connections.append(leads_to_relation.__dict__)

            prev_stop_id = stop_id

            stop = StopModel(
                id=stop_id,
                start_station_time=str(start_time),
                arrival_time_minutes=arrival_time,
                departure_time_minutes=departure_time,
                station_id=station_id
            )
            stops.append(stop.__dict__)


    save_json_file("stops", stops, RES_PATH)
    save_json_file("leads_to_relations", stops_connections, RES_PATH)
    transfers = generate_transfers(stops)
    save_json_file("transfers", transfers, RES_PATH)


if __name__ == "__main__":
    generate_schedule()
