import os
import json
import math
from Stop import Stop
from Edge import Edge
import heapq

class Graph():
   def __init__(self, stops, edges, coordinates):
      self.stops = stops # list
      self.edges = edges # dict
      self.coordinates = coordinates # dict
   
   # Dijkstra algorithm:
   def dijkstra(self, source, destination):
      # initialize a time_dict with key-value is stopId-time
      time_dict = {stop: math.inf for stop in self.stops}
      # initialize a dist_dict with key-value is stopId-distance
      dist_dict = {stop: math.inf for stop in self.stops}
      time_dict[source.stopId] = 0
      dist_dict[source.stopId] = 0
      prev = {stop: None for stop in self.stops}
      # the queue save tuples
      priority_queue = []
      heapq.heappush(priority_queue, (source.stopId, 0, 0))
      while priority_queue:
         curr_stop, curr_time, curr_dist = heapq.heappop(priority_queue)
         if curr_time > time_dict[curr_stop] and curr_dist > dist_dict[curr_stop]:
            continue
         # iterate over the edges of current node
         for edge in self.edges[curr_stop]:
            time_to_go = edge.time
            dist_to_go = edge.distance
            new_time = time_dict[curr_stop] + time_to_go
            new_distance = dist_dict[curr_stop] + dist_to_go
            to_stop = edge.getEdge('to_stop')['to_stop'].stopId
            # update new time value
            if new_time < time_dict[to_stop] and new_distance < dist_dict[to_stop]:
               time_dict[to_stop] = new_time
               dist_dict[to_stop] = new_distance
               prev[to_stop] = curr_stop
               heapq.heappush(priority_queue, (to_stop, new_time, new_distance))
      result = {}
      # reconstruct the path
      if time_dict[destination.stopId] != math.inf and dist_dict[destination.stopId] != math.inf:
            path = []
            coordinates_path = []
            current = destination.stopId
            while current != source.stopId:
               path.append(current)
               coordinates_path.append(self.coordinates[prev[current]][current])
               current = prev[current]
            path.append(source.stopId)
            path.reverse()  # reverse the path to start from the source
            coordinates_path.reverse()  # reverse the coordinates path to start from the source
            result = {'time': time_dict[destination.stopId], 'distance': dist_dict[destination.stopId], 'path': path, 'coordinate': sum(coordinates_path[::-1],[])}
            self.createGeoJson(result["coordinate"])
            return result
      else:
          print(f'Can not go from {source.stopId} to {destination.stopId}')

# forming the geojson file
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
      
      file_path = os.path.join(os.getcwd(), "Output", "GeoJsonOutput.geojson")
      with open(file_path, "w", encoding="utf-8") as file:
         file.write(formatted_geojson)
      
      print("GeoJSON data has been formed and written to GeoJsonOutput.geojson file.")
      return formatted_geojson