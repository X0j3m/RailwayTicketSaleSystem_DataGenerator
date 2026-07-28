import random
import uuid
from datetime import datetime, time, timedelta

from json_handler import *
from models import *

RES_PATH = "../../res"
DAY_SECONDS = 24 * 60 * 60

stations_dict = open_json_file("train_stations")
stations = [StationModel(**item) for item in stations_dict]

routes_dict = open_json_file("train_routes")
routes = [RouteModel(**item) for item in routes_dict]

connections_dict = open_json_file("train_stations_connections")
connections = [ConnectionModel(**item) for item in connections_dict]

compositions_dict = open_json_file("compositions")
compositions = [TrainCompositionModel(**item) for item in compositions_dict]

trains_dict = open_json_file("trains")
trains = [TrainModel(**item) for item in trains_dict]


def generate_time(time_slot: str = "random"):
    if time_slot == "random":
        time_slot = random.choice(["morning", "midday", "afternoon", "evening", "night"])
    
    if time_slot == "morning":
        hour = random.randint(6, 9)
    elif time_slot == "midday":
        hour = random.randint(11, 14)
    elif time_slot == "afternoon":
        hour = random.randint(14, 17)
    elif time_slot == "evening":
        hour = random.randint(17, 21)
    else:  # night
        hour = random.randint(22, 23) if random.random() > 0.5 else random.randint(0, 5)
    
    minute = random.randint(0, 59)
    return time(hour, minute, 0)


def get_distance(s1_id: str, s2_id: str):
    connection = next(
        conn
        for conn in connections
        if (conn.source_id == s1_id and conn.target_id == s2_id)
        or (conn.source_id == s2_id and conn.target_id == s1_id)
    )
    return connection.distance


def get_exact_dt(start_station_time_str: str, minutes_offset: int | None) -> datetime | None:
    if minutes_offset is None:
        return None

    base_time = datetime.strptime(start_station_time_str, "%H:%M:%S").time()
    base_dt = datetime(2000, 1, 1, base_time.hour, base_time.minute, base_time.second)
    return base_dt + timedelta(minutes=minutes_offset)


def calculate_waiting_time(stop1: dict, stop2: dict) -> int:
    arrival_offset1 = (
        stop1['arrival_time_minutes']
        if stop1['arrival_time_minutes'] is not None
        else stop1['departure_time_minutes']
    )
    dt1 = get_exact_dt(stop1['start_station_time'], arrival_offset1)

    departure_offset2 = (
        stop2['departure_time_minutes']
        if stop2['departure_time_minutes'] is not None
        else stop2['arrival_time_minutes']
    )
    dt2 = get_exact_dt(stop2['start_station_time'], departure_offset2)

    if dt1 is None or dt2 is None:
        return -1

    if dt2 < dt1:
        dt2 += timedelta(days=1)

    diff_in_minutes = int((dt2 - dt1).total_seconds() / 60)

    if diff_in_minutes <= 0:
        return -1

    return diff_in_minutes


def generate_transfers(stops):
    transfers = []

    stops_by_station = {}
    for stop in stops:
        station_id = stop['station_id']
        stops_by_station.setdefault(station_id, []).append(stop)

    print(f"ALL STATIONS: {len(stations)}")
    print(f"SCHEDULE STATIONS: {len(stops_by_station)}")

    for iterator, (station, station_stops) in enumerate(stops_by_station.items(), 1):
        print(f"{iterator}. STATION_STOPS: {len(station_stops)}")

        for i, stop_from in enumerate(station_stops):
            for j, stop_to in enumerate(station_stops):
                if i != j:
                    waiting_time = calculate_waiting_time(stop_from, stop_to)
                    if 0 <= waiting_time <= 6 * 60:
                        transfer = TransferRelationModel(
                            id=str(uuid.uuid4()),
                            from_stop_id=stop_from['id'],
                            to_stop_id=stop_to['id'],
                            time=waiting_time
                        )
                        transfers.append(transfer.__dict__)

    return transfers


def generate_schedule():
    stops = []
    stops_connections = []
    
    prioritized_routes = ensure_major_connections(list(routes))
    
    used_compositions = []
    available_compositions = list(compositions)
    
    routes_processed = 0
    routes_skipped = 0
    
    trains_per_route = random.randint(2, 4)
    
    for route in prioritized_routes:
        for train_num in range(trains_per_route):
            if not available_compositions:
                if used_compositions:
                    available_compositions = list(used_compositions)
                    used_compositions = []
                else:
                    routes_skipped += 1
                    continue
            
            train_composition = available_compositions.pop(random.randrange(len(available_compositions)))
            used_compositions.append(train_composition)
            train_composition_id = train_composition.id
            
            train = next(item for item in trains if item.id == train_composition.train_id)
            train_velocity = train.velocity
            
            time_slot = ["morning", "midday", "afternoon", "evening"][train_num % 4]
            start_time = generate_time(time_slot)
            trip_time = 0
            prev_stop_id = None
            prev_departure_time = 0
            
            for i, station_id in enumerate(route.route):
                stop_id = str(uuid.uuid4())
                stop_minutes = random.randint(1, 10)
                
                if station_id == route.start_station_code:
                    arrival_time = None
                    departure_time = trip_time
                    prev_departure_time = departure_time
                    
                    if i + 1 < len(route.route):
                        next_station_id = route.route[i + 1]
                        distance_to_next_station = get_distance(station_id, next_station_id)
                        trip_time += round((distance_to_next_station / train_velocity) * 60)
                
                else:
                    if station_id != route.end_station_code:
                        arrival_time = trip_time
                        trip_time += stop_minutes
                        prev_departure_time = departure_time
                        departure_time = trip_time
                        
                        if i + 1 < len(route.route):
                            next_station_id = route.route[i + 1]
                            distance_to_next_station = get_distance(station_id, next_station_id)
                            trip_time += round((distance_to_next_station / train_velocity) * 60)
                    else:
                        arrival_time = trip_time
                        prev_departure_time = departure_time
                        departure_time = None
                    
                    if prev_stop_id is not None:
                        leads_to_relation = LeadsToRelationModel(
                            id=str(uuid.uuid4()),
                            from_stop_id=prev_stop_id,
                            to_stop_id=stop_id,
                            time=arrival_time - prev_departure_time,
                        )
                        stops_connections.append(leads_to_relation.__dict__)
                
                prev_stop_id = stop_id
                
                stop = StopModel(
                    id=stop_id,
                    start_station_time=str(start_time),
                    arrival_time_minutes=arrival_time,
                    departure_time_minutes=departure_time,
                    station_id=station_id,
                    train_composition_id=train_composition_id,
                )
                stops.append(stop.__dict__)
            
            routes_processed += 1
    
    save_json_file("stops", stops)
    save_json_file("leads_to_relations", stops_connections)
    
    transfers = generate_transfers(stops)
    save_json_file("transfers", transfers)
    
    stations_covered, cities_coverage = analyze_network_coverage(stops)
    
    print(f"\n=== NETWORK COVERAGE STATISTICS ===")
    print(f"Total stations in dataset: {len(stations)}")
    print(f"Stations with active schedules: {len(stations_covered)}")
    print(f"Total possible routes: {len(routes)}")
    print(f"Routes processed: {routes_processed}")
    print(f"Routes skipped: {routes_skipped}")
    print(f"Coverage percentage: {(routes_processed / len(routes) * 100):.1f}%")
    print(f"Total stops created: {len(stops)}")
    print(f"Total connections created: {len(stops_connections)}")
    print(f"Total transfers created: {len(transfers)}")


def analyze_network_coverage(stops_data):
    stations_with_stops = set()
    for stop in stops_data:
        stations_with_stops.add(stop['station_id'])
    
    cities_coverage = {}
    for station in stations:
        if station.id in stations_with_stops:
            city = station.city
            cities_coverage[city] = cities_coverage.get(city, 0) + 1
    
    print(f"\n=== CITIES COVERAGE ===")
    print(f"Cities with rail connections: {len(cities_coverage)}")
    print(f"Top 10 cities by stops:")
    for city, count in sorted(cities_coverage.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {city}: {count} stations")
    
    return stations_with_stops, cities_coverage


def get_major_cities():
    major_cities = [
        "Warszawa", "Kraków", "Gdańsk", "Poznań", "Wrocław",
        "Szczecin", "Łódź", "Toruń", "Białystok", "Katowice"
    ]
    return [s for s in stations if s.city in major_cities]


def ensure_major_connections(routes_list):
    """Prioritize routes connecting major Polish cities."""
    major_stations = get_major_cities()
    major_ids = {s.id for s in major_stations}
    
    major_routes = [r for r in routes_list if r.start_station_code in major_ids or r.end_station_code in major_ids]
    other_routes = [r for r in routes_list if r.start_station_code not in major_ids and r.end_station_code not in major_ids]
    
    return major_routes + other_routes


# if __name__ == "__main__":
#     generate_schedule()