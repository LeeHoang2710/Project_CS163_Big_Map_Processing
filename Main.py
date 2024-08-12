import os
import json
import random
from datetime import datetime
from Path import *
from Stop import *
from RouteVar import *
from Edge import *
from Graph import *
from HubLabeling import *
from ContractionHierachies import *
from TransitNodeRouting import *

print("...........Handling data ...........")
pathquery = PathQuery()
stopquery = StopQuery()
routevarquery = RouteVarQuery()
edgequery = EdgesQuery()

data_dir = os.path.join(os.getcwd(), "Database")
path_dir = os.path.join(data_dir, 'paths.json')
stop_dir = os.path.join(data_dir, 'stops.json')
route_dir = os.path.join(data_dir, 'vars.json')
importance_dir = os.path.join(os.getcwd(), "Output", "4397-Important.json")
path_dict = pathquery.readPathData(path_dir)
# {route_id: {var_id: [coordinates, ...], var_id: [...]}, route_id: {...}}
print(".....Reading path data complete......")
stop_dict = stopquery.readStopData(stop_dir)
# {route_id: {var_id: [stop1, stop2, ...], var_id: [...]}, route_id: {...}}
print(".....Reading stop data complete......")
route_dict = routevarquery.readRouteData(route_dir)
# {route_id: {var_id: [distance, time], var_id: [...]}, route_id: {...}}
print(".....Reading route data complete.....")
edges, coordinates = edgequery.handleData(stopquery, pathquery, route_dict, stop_dict)
stop_nodes = set(stop.getStop('stopId')['stopId'] for stop in stopquery.stops)
stop_nodes = list(stop_nodes)
bus_graph = Graph(stops=stop_nodes, edges=edges, coordinates = coordinates)
print("......Handling edges complete.......")


def checkResults(file1, file2):
   try:
      with open(file1, 'r') as f1, open(file2, 'r') as f2:
         content1 = json.load(f1)
         content2 = json.load(f2)
         if content1 == content2:
            print(f"{file1} and {file2} are the same")
   except Exception as e:
      print(f"An error occurred: {e}")

# new_graph = HubLabeling(graph=bus_graph, importance={})
# new_graph.importance = new_graph.computeImportance(importance_dir)
# labels = new_graph.hubLabeling(new_graph.importance)
# print("......Hub labeling complete......")
# result = new_graph.queryPath(source=35, destination=2755, labels=labels)
# finding_stops = stopquery.searchByABC(stopId=35)
# source_name = finding_stops[0].getStop('name')['name']
# finding_stops = stopquery.searchByABC(stopId=2755)
# destination_name = finding_stops[0].getStop('name')['name']
# print(f"Shortest path from {source_name} to {destination_name}: {result}")


# source = 35
# destination = 2189
# shortest_path, time = bus_graph.dijkstraQuery(source , destination)
# print(f"Shortest path from {source} to {destination}: {shortest_path}")
# print(f"Time taken for a query: {time} seconds")


# bus_graph.dijkstraAllStops()
# bus_graph.dijkstraKImportant(len(stop_nodes))

# shortest_path = bus_graph.aStar(source = 718, destination  = 704)
# print(f"Shortest path from {source} to {destination}: {shortest_path}")




new_graph = ContractionHierachies(stops=stop_nodes, edges=edges, n=7800)
new_graph.buildNeighborsAndCosts()
vertices = new_graph.preProcess()
print("......Contraction Hierachies complete......")
result = new_graph.queryBidirectional(source=2, target=2755)
print(f"Shortest path from 2 to 2755: {result[2]}")
result = bus_graph.dijkstraQuery(source=2, destination=2755)
print(f"Shortest path from 2 to 2755: {result[2]}")

tnr_graph = TNRGraph(vertices=vertices, graph=new_graph)
tnr_graph.computeTNR(count=100)
result=tnr_graph.queryWithTNR(source=2, target=2755)
print(f"Shortest path from 2 to 2755: {result[1]}")


# sum1 = 0
# sum2 = 0
# count = 0
# resultsCH = []
# resultsNormal = []
# for i in range(10000):
#    source = random.choice(stop_nodes)
#    destination = random.choice(stop_nodes)
#    while destination == source:
#       destination = random.choice(stop_nodes)
#    result1, time1, path1 = new_graph.queryBidirectional(source=source, target=destination)
#    resultsCH.append([source, destination, result1, path1])
#    sum1 += time1

#    result2, time2, path2 = bus_graph.dijkstraQuery(source, destination)
#    resultsNormal.append([source, destination, result2, path2])
#    sum2 += time2

#    if path1 != path2:
#       count += 1


# print(f"Time taken for all queries of CH: {sum1} seconds")
# print(f"Time taken for a query of CH: {sum1 / 10000} seconds")


# print(f"Time taken for all queries of Normal: {sum2} seconds")
# print(f"Time taken for a query of Normal: {sum2 / 10000} seconds")


# with(open('Output/ResultsCH.json', 'w')) as file:
#    json.dump(resultsCH, file, ensure_ascii=False, indent=4)
#    print("Result file of CH created")


# with(open('Output/ResultsNormal.json', 'w')) as file:
#    json.dump(resultsNormal, file, ensure_ascii=False, indent=4)
#    print("Result file of Normal created")

# checkResults('Output/ResultsCH.json', 'Output/ResultsNormal.json')
# print(f"Number of different paths: {count}")