import math
import json
from Stop import *

class Edge():
   def __init__(self, from_stop, to_stop, name, coordinates_path, distance, time):
      self.from_stop = from_stop
      self.to_stop = to_stop
      self.name = name
      self.coordinates = coordinates_path
      self.distance = distance
      self.time = time


   def to_dict(self):
        return {
            'from_stop': self.from_stop.getStop('stopId')['stopId'], 
            'to_stop': self.to_stop.getStop('stopId')['stopId'],
            'name': self.name,
            'coordinates': self.coordinates,
            'distance': self.distance,
            'time': self.time
         }
   
   def getEdge(self, *argv):
      result = {}
      allowed_properties = list(self.__dict__.keys())
      for arg in argv:
         if arg not in allowed_properties:
               raise ValueError(f"Invalid property {arg} in the property of Stop" + '\n' + f"Properties should look for {allowed_properties}")
         else:
            result[arg] = getattr(self, arg)
      return result

   def setEdge(self, **kwargs):
      allowed_properties = list(self.__dict__.keys())
      for key, value in kwargs.items():
         if key not in allowed_properties:
               raise ValueError(f"Invalid property: {key}")
         
      for key, value in kwargs.items():
         setattr(self, key, value)        
         print("Successfully reset the Edge instance")

class EdgesQuery():
   def __init__(self):
      self.edges = {}

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
   
   def edgesDistance(self, coordinates):
      distance = 0
      for i in range(0, len(coordinates)-1):
         lat1, lng1 = coordinates[i]
         lat2, lng2 = coordinates[i+1]
         distance += self.pointsDistance(lat1, lng1, lat2, lng2)
      return distance
   
   def findClosestCoordinateIndex(self, coordinates, target_lat, target_lng):
      # assign the length of coordinates list --> index variable
      return min(range(len(coordinates)), key=lambda index: self.pointsDistance(coordinates[index][1], coordinates[index][0], target_lat, target_lng))

   def handleData(self, stopquery, pathquery, route_dict, stop_dict):
      coordinates_dict = {}
      counter = 0
      edges_dict = {stop.getStop('stopId')['stopId']:[] for stop in stopquery.stops}
      # {'stopId': []}
      for path in pathquery.paths:
         path_info = path.getPath('routeId', 'routeVarId', 'coordinates')
         coordinates = path_info['coordinates']
         path_distance, path_runningtime = route_dict[path_info['routeId']][path_info['routeVarId']]
         path_average_velocity = path_distance / path_runningtime

         # retrieve all stops that match routeId and varId
         stops = stop_dict[path_info['routeId']][path_info['routeVarId']]

         for i in range(len(stops) - 1):
            stop_from = stops[i]
            stop_from_id = stop_from.getStop('stopId')['stopId']
            stop_to = stops[i + 1]
            stop_to_id = stop_to.getStop('stopId')['stopId']
            name = [stop_from.getStop('name')['name'], stop_to.getStop('name')['name']]
            
            lat_from = stop_from.getStop('lat')['lat']
            lng_from = stop_from.getStop('lng')['lng']
            lat_to = stop_to.getStop('lat')['lat']
            lng_to = stop_to.getStop('lng')['lng']

            index1 = self.findClosestCoordinateIndex(coordinates, lat_from, lng_from)
            index2 = self.findClosestCoordinateIndex(coordinates,lat_to, lng_to)

            # the path on coordinates is the subset from tuple(index1) to tuple(index2)
            coordinates_path = coordinates[index1:index2+1]
            distance = self.edgesDistance(coordinates_path)
            time = distance / path_average_velocity

            # initialize a new edge from stop_from and stop_to
            if stop_from_id not in coordinates_dict:
               # Initialize as empty dictionary
               coordinates_dict[stop_from_id] = {}
               coordinates_dict[stop_from_id][stop_to_id] = coordinates_path
               newEdge = Edge(stop_from, stop_to, name, coordinates_path, distance, time)
               edges_dict[stop_from_id].append(newEdge)
               counter += 1
            else:
               if stop_to_id not in coordinates_dict[stop_from_id]:
                  coordinates_dict[stop_from_id][stop_to_id] = coordinates_path
                  newEdge = Edge(stop_from, stop_to, name, coordinates_path, distance, time)
                  edges_dict[stop_from_id].append(newEdge)
                  counter += 1
               else:
                  existing_distance = self.edgesDistance(coordinates_dict[stop_from_id][stop_to_id])
                  if distance < existing_distance:
                     coordinates_dict[stop_from_id][stop_to_id] = coordinates_path
                     # Find and update the existing edge in edges_dict
                     for edge in edges_dict[stop_from_id]:
                        if edge.to_stop.getStop('stopId')['stopId'] == stop_to_id:
                            edge.coordinates = coordinates_path
                            edge.distance = distance
                            edge.time = time
                            break
         self.edges = edges_dict



      # edges_dict_serializable = {k: [edge.to_dict() for edge in v] for k, v in self.edges.items()}
      # with open('./Output/Edges.json', 'w') as file:
      #    json.dump(edges_dict_serializable, file, ensure_ascii=False, indent=4)
      #    print(f"Edges data saved")
      # print(f"Total number of edges: {counter}")
      return edges_dict, coordinates_dict  
   