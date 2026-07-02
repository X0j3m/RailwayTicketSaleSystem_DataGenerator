import networkx as nx
import random
from common.json_handler import *
from common.models import *

NUMBER_OF_PATHS = 1


def create_connections_graph(connections_list):
    G = nx.Graph()

    edges_dict = [
        (edge.source_id, edge.target_id)
        for edge in connections_list
    ]

    print(edges_dict)
    G.add_edges_from(edges_dict)
    return G


def pick_random_route(nodes):
    route = random.sample(nodes, 2)
    return route


stations_dict = open_json_file("train_stations")
stations = [StationModel(**item) for item in stations_dict]

connections_dict = open_json_file("train_stations_connections")
connections = [ConnectionModel(**item) for item in connections_dict]

print(connections)
graph = create_connections_graph(connections)
graph_diameter = nx.diameter(graph)
print("Graph diameter: ", graph_diameter)

nodes = list(graph.nodes)

for _ in range(NUMBER_OF_PATHS):
    start, end = pick_random_route(nodes)
    print("ROUTES FOR: ", start, end)
    max_num_of_nodes = graph_diameter//2
    paths_iterator = nx.all_simple_paths(graph,
                                         source=start,
                                         target=end,
                                         cutoff=max_num_of_nodes - 1)

    for path in paths_iterator:
        print(path)
