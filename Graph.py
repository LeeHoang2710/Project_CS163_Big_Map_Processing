import os
import json
import math
from Stop import Stop
from Edge import Edge
from datetime import datetime
import heapq

class Graph():
   def __init__(self, stops, edges, coordinates):
      self.stops = stops # list
      self.edges = edges # dict
      self.coordinates = coordinates # dict
   
   # Dijkstra algorithm:
   def dijkstraOriginal(self, source):
      start_time = datetime.now()
      # time_dict = {stop: math.inf for stop in self.stops}
      dist_dict = {stop: math.inf for stop in self.stops}
      # time_dict[source] = 0
      dist_dict[source] = 0
      prev = {stop: None for stop in self.stops}
      priority_queue = []
      heapq.heappush(priority_queue, (source, 0))
      while priority_queue:
         curr_stop, curr_dist = heapq.heappop(priority_queue)
         if curr_dist > dist_dict[curr_stop]:
            continue
         for edge in self.edges[curr_stop]:
            # time_to_go = edge.time
            # new_time = time_dict[curr_stop] + time_to_go
            new_distance = dist_dict[curr_stop] + edge.distance
            to_stop = edge.getEdge('to_stop')['to_stop'].stopId
            if new_distance < dist_dict[to_stop]:
               # time_dict[to_stop] = new_time
               dist_dict[to_stop] = new_distance
               prev[to_stop] = curr_stop
               heapq.heappush(priority_queue, (to_stop, new_distance))


      end_time = datetime.now()
      print(f"Total time: {(end_time - start_time).total_seconds()} seconds")
      return dist_dict

      # result = {}
      # for destination in self.stops:
      #    if time_dict[destination] != math.inf and destination != source:
      #       temp = destination
      #       path = []
      #       while temp != source:
      #          path.append(temp)
      #          temp = prev[temp]
      #       path.append(source)
      #       path.reverse()
      #       result[destination] = {'time': time_dict[destination], 'distance': dist_dict[destination], 'path': path}
      # return result

   def dijkstraFindPath(self, source, destination):
      # initialize a time_dict with key-value is stopId-time
      time_dict = {stop: math.inf for stop in self.stops}
      # initialize a dist_dict with key-value is stopId-distance
      dist_dict = {stop: math.inf for stop in self.stops}
      time_dict[source] = 0
      dist_dict[source] = 0
      prev = {stop: None for stop in self.stops}
      # the queue save tuples
      priority_queue = []
      heapq.heappush(priority_queue, (source, 0, 0))
      start_time = datetime.now()
      while priority_queue:
         curr_stop, curr_time, curr_dist = heapq.heappop(priority_queue)
         if curr_dist > dist_dict[curr_stop]:
            continue
         # iterate over the edges of current node
         for edge in self.edges[curr_stop]:
            time_to_go = edge.time
            dist_to_go = edge.distance
            new_time = time_dict[curr_stop] + time_to_go
            new_distance = dist_dict[curr_stop] + dist_to_go
            to_stop = edge.getEdge('to_stop')['to_stop'].stopId
            # update new time value
            if new_distance < dist_dict[to_stop]:
               time_dict[to_stop] = new_time
               dist_dict[to_stop] = new_distance
               prev[to_stop] = curr_stop
               heapq.heappush(priority_queue, (to_stop, new_time, new_distance))
      result = {}
      # reconstruct the path
      if time_dict[destination] != math.inf and dist_dict[destination] != math.inf:
            path = []
            coordinates_path = []
            current = destination
            while current != source:
               path.append(current)
               coordinates_path.append(self.coordinates[prev[current]][current])
               current = prev[current]
            path.append(source)
            path.reverse()  # reverse the path to start from the source
            coordinates_path.reverse()  # reverse the coordinates path to start from the source
            end_time = datetime.now()
            print(f"Total time: {(end_time - start_time).total_seconds()} seconds")
            result = {'time': time_dict[destination], 'distance': dist_dict[destination], 'path': path}
            geoMap = {'coordinate': sum(coordinates_path[::-1],[])}
            self.createGeoJson(geoMap["coordinate"])
            return result
      else:
          print(f'Can not go from {source.stopId} to {destination.stopId}')


   def dijkstraQuery(self, source, destination):
        # Initialization
        dist_dict = {stop: math.inf for stop in self.stops}
        dist_dict[source] = 0
        priority_queue = []
        heapq.heappush(priority_queue, (0, source))
        visited = set()
        
        start_time = datetime.now()

        while priority_queue:
            curr_dist, curr_stop = heapq.heappop(priority_queue)
            
            # Early exit if destination is reached
            if curr_stop == destination:
                end_time = datetime.now()
                total_time = (end_time - start_time).total_seconds()
                return round(dist_dict[destination], 4), total_time
            
            # Skip processing if the node is already visited
            if curr_stop in visited:
                continue
            visited.add(curr_stop)

            # Relaxation of edges
            for edge in self.edges[curr_stop]:
                to_stop = edge.getEdge('to_stop')['to_stop'].stopId
                new_distance = curr_dist + edge.distance
                if new_distance < dist_dict[to_stop]:
                    dist_dict[to_stop] = new_distance
                    heapq.heappush(priority_queue, (new_distance, to_stop))

        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds()

        # If the destination is not reachable, return -1
        return round(-1 if dist_dict[destination] == math.inf else dist_dict[destination], 4), total_time



   def dijkstraAllStops(self):
      start_time = datetime.now()
      all_shortest_paths = {}
      file_path = os.path.join(os.getcwd(), "Output", "AllShortestPaths.json")
      count = 0
      sum = 0
      for stop in self.stops:
         run_start = datetime.now()
         result = self.dijkstraOriginal(stop)
         run_end = datetime.now()
         run_period = (run_end - run_start).total_seconds()
         sum += run_period
         all_shortest_paths[stop] = result
         count += 1
         print(f"____Processed {count} stop/total {len(self.stops)} stops____")
      end_time = datetime.now()
      total_time = (end_time - start_time).total_seconds()
      with open(file_path, "w", encoding="utf-8") as file:
         json.dump(all_shortest_paths, file, indent=4)
      print("All shortest paths have been written to json file.")
      print("Finished all stops")
      print(f"Total time: {total_time} seconds") #Total time: 214.527972 seconds


   def dijkstraKImportant(self, k):
      start_time = datetime.now()
      file_path = os.path.join(os.getcwd(), "Output", f"{k}-Important.json")
      importance = {stop: 0 for stop in self.stops}
      for stop in self.stops:
         result = self.dijkstraOriginal(stop)
         for stopId in result:
            for stop in result[stopId]['path']:
               importance[stop] += 1

      sorted_importance = {k: v for k, v in sorted(importance.items(), key=lambda item: item[1], reverse=True)}
      top_k = {stop: sorted_importance[stop] for stop in list(sorted_importance.keys())[:k]}
      end_time = datetime.now()
      total_time = (end_time - start_time).total_seconds()
      print(f"Total time: {total_time} seconds")

      with open(file_path, "w", encoding="utf-8") as file:
         json.dump(top_k, file, indent=4)
      return top_k


   # A* algorithm:
   def pointsDistance(self, lat1, lng1, lat2, lng2):
      # Convert latitude and lnggitude from degrees to radians
      lat1_rad = math.radians(lat1)
      lng1_rad = math.radians(lng1)
      lat2_rad = math.radians(lat2)
      lng2_rad = math.radians(lng2)
      
      # Calculate the differences in latitude and lnggitude
      dlat = lat2_rad - lat1_rad
      dlng = lng2_rad - lng1_rad
      
      # Apply the Haversine formula
      a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlng / 2)**2
      c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
      
      # Earth's radius in kilometers (use 3956 for miles)
      r = 6371
      distance_km = r * c
      return distance_km
   
   def heuristic(self, stop1, stop2):
      edge1 = self.coordinates[stop1]
      for i in edge1:
         coordinates1 = self.coordinates[stop1][i][0]
         break
      edge2 = self.coordinates[stop2]
      for i in edge2:
         coordinates2 = self.coordinates[stop2][i][0]
         break
      distance = self.pointsDistance(coordinates1[1], coordinates1[0], coordinates2[1], coordinates2[0])
      return distance
   
   def aStar(self, source, destination):
      start_time = datetime.now()
      dist_dict = {stop: math.inf for stop in self.stops}
      time_dict = {stop: math.inf for stop in self.stops}
      dist_dict[source] = 0
      time_dict[source] = 0
      prev = {stop: None for stop in self.stops}
      priority_queue = [(self.heuristic(source, destination), source)]
      visited = set()
      while priority_queue:
         _, curr_stop = heapq.heappop(priority_queue)
         if curr_stop in visited:
            continue
         visited.add(curr_stop)
         # print(curr_stop)
         if curr_stop == destination:
            break
         for edge in self.edges[curr_stop]:
            new_distance = dist_dict[curr_stop] + edge.distance
            new_time = time_dict[curr_stop] + edge.time
            # print(new_distance)
            to_stop = edge.getEdge('to_stop')['to_stop'].stopId
            if new_distance < dist_dict[to_stop]:
               dist_dict[to_stop] = new_distance
               time_dict[to_stop] = new_time
               prev[to_stop] = curr_stop
               addition = self.heuristic(to_stop, destination)
               heapq.heappush(priority_queue, (new_distance + addition, to_stop))

      path = []
      current = destination
      while current is not None:
         path.append(current)
         current = prev[current]
      path.reverse()
      end_time = datetime.now()
      print(f"Total time: {(end_time - start_time).total_seconds()} seconds")
      result = {'time': time_dict[destination],'distance': dist_dict[destination], 'path': path}
      return result
   

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
