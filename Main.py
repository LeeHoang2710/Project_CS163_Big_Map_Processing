import os
from Path import *
from Stop import *
from RouteVar import *
from Edge import *
from Graph import *

print("...........Handling data ...........")
pathquery = PathQuery()
stopquery = StopQuery()
routevarquery = RouteVarQuery()
edgequery = EdgesQuery()

data_dir = os.path.join(os.getcwd(), "database")
path_dir = os.path.join(data_dir, 'paths.json')
stop_dir = os.path.join(data_dir, 'stops.json')
route_dir = os.path.join(data_dir, 'vars.json')
path_dict = pathquery.readPathData(path_dir)
# {route_id: {var_id: [coordinates, ...], var_id: [...]}, route_id: {...}}
print(".....Reading path data complete......")
stop_dict = stopquery.readStopData(stop_dir)
# {route_id: {var_id: [stop1, stop2, ...], var_id: [...]}, route_id: {...}}
print(".....Reading stop data complete......")
route_dict = routevarquery.readRouteData(route_dir)
# {route_id: {var_id: [distance, time], var_id: [...]}, route_id: {...}}
print(".....Reading route data complete.....")
edges, coodinates = edgequery.handleData(stopquery, pathquery, route_dict, stop_dict)
stop_nodes = set(stop.getStop('stopId')['stopId'] for stop in stopquery.stops)
bus_graph = Graph(stops=stop_nodes, edges=edges, coordinates = coodinates)
print("......Handling edges complete.......")


# route_id = '81'
# var_id = '1'
# stopquery.stops = stop_dict[route_id][var_id]
# source = stopquery.searchByABC(stopId=1904)
# destination = stopquery.searchByABC(stopId=2360)
# print(source[0].name)
# print(destination[0].name)
# shortest_path = bus_graph.dijkstra(source[0], destination[0])
# print(shortest_path['path'])
# print(shortest_path['time'] * 60)
# print(shortest_path['distance'])

bus_graph.dijkstraAllStops()