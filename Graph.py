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
      # initialize a time_dict with key-value is stop-time
      time_dict = {stop: math.inf for stop in self.stops}
      time_dict[source.stopId] = 0
      prev = {stop: None for stop in self.stops}
      # the queue save tuples
      priority_queue = []
      heapq.heappush(priority_queue, (source.stopId, 0))
      while priority_queue:
         curr_stop, curr_dist = heapq.heappop(priority_queue)
         if curr_dist > time_dict[curr_stop]:
            continue
         # iterate over the edges of current node
         for edge in self.edges[curr_stop]:
            time_to_go = edge.time
            new_time = time_dict[curr_stop] + time_to_go
            to_stop = edge.getEdge('to_stop')['to_stop'].stopId
            # update new time value
            if new_time < time_dict[to_stop]:
               time_dict[to_stop] = new_time
               prev[to_stop] = curr_stop
               heapq.heappush(priority_queue, (to_stop, new_time))
      result = {}
      # reconstruct the path
      if time_dict[destination.stopId] != math.inf:
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
            result = {'time': time_dict[destination.stopId], 'path': path, 'coordinate': sum(coordinates_path[::-1],[])}
            self.createGeoJson(result["coordinate"])
            return result
      else:
          print(f'Can not go from {source} to {destination}')

