import heapq
import math
import json
from datetime import datetime
import os

class HubLabeling:
   def __init__(self, graph):
      self.graph = graph
      self.importance = {}
         
   def computeImportance(self, file_path):
      self.importance = {}
      with open(file_path, 'r') as file:
         data = json.load(file)
         self.importance = data
      return self.importance


   def dijkstra(self, source):
    dist_dict = {stop: math.inf for stop in self.graph.stops}
    dist_dict[source] = 0
   #  prev = {stop: None for stop in self.graph.stops}
    priority_queue = [(0, source)]
    
    
    while priority_queue:
        curr_dist, curr_stop = heapq.heappop(priority_queue)
        if curr_dist > dist_dict[curr_stop]:
            continue
        
        for edge in self.graph.edges[curr_stop]:
            to_stop = edge.getEdge('to_stop')['to_stop'].stopId
            new_distance = curr_dist + edge.distance
            if new_distance < dist_dict[to_stop]:
                dist_dict[to_stop] = new_distance
               #  prev[to_stop] = curr_stop
                heapq.heappush(priority_queue, (new_distance, to_stop))

    return dist_dict
   
   def hubLabeling(self):
      labels = {i: {'in': {}, 'out': {}, 'path': {}} for i in range(8000)}

      start_time = datetime.time()
      for stopId in self.graph.stops:
         dist_dict = self.dijkstra(stopId)
         for targetId, dist in dist_dict.items():
               if dist != math.inf:
                  labels[stopId]['out'][targetId] = dist
                  labels[targetId]['in'][stopId] = dist
                  # Store the path
                  # path = []
                  # currentId = targetId
                  # while currentId is not None:
                  #    path.append(currentId)
                  #    currentId = prev[currentId]
                  # labels[stopId]['path'][targetId] = path[::-1]
      end_time = datetime.time()
      print(f"Time taken for labeling: {(end_time - start_time).total_seconds()} seconds")

      return labels
      
   def queryPath(self, source, destination, labels):
      source_labels = labels[source]['out']
      destination_labels = labels[destination]['in']
      
      start_time = datetime.time()
      shared_hubs = set(source_labels.keys()).intersection(set(destination_labels.keys()))
      shortest_dist = math.inf
      shortest_path = []
      coordinates_path = []
      best_hub = None
      
      for hub in shared_hubs:
         if source_labels[hub] + destination_labels[hub] < shortest_dist:
            shortest_dist = source_labels[hub] + destination_labels[hub]
            best_hub = hub

      # if best_hub is not None:
      # # Reconstruct the path 
      #    shortest_path = labels[source]['path'][best_hub] + labels[best_hub]['path'][destination][1:]
      #    # Avoid duplicating the hub
      #    coordinates_path = [self.graph.coordinates[shortest_path[i]][shortest_path[i+1]] for i in range(len(shortest_path)-1)]
               
      end_time = datetime.time()
      total_time = (end_time - start_time).total_seconds()
      return -1 if shortest_dist == math.inf else shortest_dist, total_time
      # print(f"Time taken for query: {(end_time - start_time).total_seconds()} seconds")
      # print(f"Shortest path: {shortest_path}")

      #    self.createGeoJson(sum(coordinates_path[::-1],[]))
         
      # else:
      #    print("No path found")

      # return {"from - to": [source, destination], "shortest_dist": shortest_dist, "coordinates_path": coordinates_path}

   

   def createGeoJson(self, coordinates):
      if coordinates == []:
         return None
      start_point = coordinates[0]
      end_point = coordinates[-1]

      line_string_geometry = {
         "type": "LineString",
         "coordinates": coordinates
      }
      
      start_point_geometry = {
         "type": "Point",
         "coordinates": start_point
      }
      
      end_point_geometry = {
         "type": "Point",
         "coordinates": end_point
      }

      line_string_feature = {
         "type": "Feature",
         "geometry": line_string_geometry,
         "properties": {
               "Type": "LineString"
         }
      }
      
      start_point_feature = {
         "type": "Feature",
         "geometry": start_point_geometry,
         "properties": {
               "Type": "StartPoint"
         }
      }
      
      end_point_feature = {
         "type": "Feature",
         "geometry": end_point_geometry,
         "properties": {
               "Type": "EndPoint"
         }
      }

      geojson_data = {
         "type": "FeatureCollection",
         "features": [line_string_feature, start_point_feature, end_point_feature]
      }
      
      formatted_geojson = json.dumps(geojson_data, indent=4)
      
      file_path = os.path.join(os.getcwd(), "Output", "GeoJsonOutputNew.geojson")
      with open(file_path, "w", encoding="utf-8") as file:
         file.write(formatted_geojson)
      
      print("GeoJSON data has been formed and written to GeoJsonOutputNew.geojson file.")
      return formatted_geojson
