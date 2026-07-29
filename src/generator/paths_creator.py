import networkx as nx
import random
from json_handler import *
from models import *
import uuid

NUMBER_OF_PATHS = 60

def create_connections_graph(connections_list):
    G = nx.Graph()

    edges_dict = [
        (edge.source_id, edge.target_id, edge.distance)
        for edge in connections_list
    ]

    G.add_weighted_edges_from(edges_dict)
    return G


def pick_random_route(nodes):
    route = random.sample(nodes, 2)
    return route


stations_dict = open_json_file("train_stations")
stations = [StationModel(**item) for item in stations_dict]

connections_dict = open_json_file("train_stations_connections")
connections = [ConnectionModel(**item) for item in connections_dict]

graph = create_connections_graph(connections)
graph_diameter = nx.diameter(graph)


def convert_to_route(path, path_weight):
    start_station = [s for s in stations if s.id == path[0]][0]
    end_station = [s for s in stations if s.id == path[-1]][0]
    route = RouteModel(
        id=str(uuid.uuid4()),
        start_station=start_station.name,
        end_station=end_station.name,
        start_station_code=path[0],
        end_station_code=path[-1],
        route=path,
        distance=path_weight
    )

    return route


def generate_paths():
    print("GENERATING PATHS")
    nodes = list(graph.nodes)

    min_num_of_stations = int(graph_diameter * 0.4)
    max_num_of_stations = int(graph_diameter)

    print(f"GRAPH DIAMETER: {graph_diameter}")

    generated_routes = []
    while len(generated_routes) < NUMBER_OF_PATHS:
        max_num_of_nodes = random.randint(min_num_of_stations, max_num_of_stations)
        start, end = pick_random_route(nodes)
        paths_iterator = nx.all_simple_paths(graph,
                                             source=start,
                                             target=end,
                                             cutoff=max_num_of_nodes)

        max_path_length = 0
        max_path = []
        path_weight = 0
        for path in paths_iterator:
            if len(path) > max_path_length:
                path_weight = sum(graph[path[i]][path[i + 1]]["weight"] for i in range(len(path) - 1))
                max_path_length = len(path)
                max_path = path

        if max_path not in ([], None) and max_path_length >= 3:
            route = convert_to_route(max_path, path_weight)
            generated_routes.append(route)

    routes_dict = [obj.model_dump() for obj in generated_routes]
    save_json_file("train_routes", routes_dict)

    print("PATHS GENERATED")
    return generated_routes

# if __name__ == "__main__":
#     paths = generate_paths()
#     for path in paths:
#         for i, node in enumerate(path.route):
#             station = [s for s in stations if s.id == node][0]
#             if i != 0:
#                 print(" -> ", end='')
#             print(f"{station.city}", end='')
#
#         print()
