import heapq
import math
import json
from datetime import datetime
from TransitNodeRouting import Vertex
from collections import deque

class Shortcut:
   def __init__(self, from_stop, to_stop, distance):
      self.from_stop = from_stop
      self.to_stop = to_stop
      self.distance = distance

class ContractionHierachies:
   def __init__(self, stops, edges, n):
      self.n = n
      self.q = []
      self.stops = stops
      self.edges = edges
      self.bidirect = [[math.inf] * n, [math.inf] * n]
      self.visited = [False] * n
      self.rank = [math.inf] * n
      self.level = [0] * n
      self.neighbors = {stop: {'incoming': [], 'outgoing': []} for stop in self.stops}  
      self.contracted = {}
      self.forwardPathTrace = {}
      self.backwardPathTrace = {}
      self.count = 0

   def buildNeighborsAndCosts(self):
      for stop, edges in self.edges.items():
         for edge in edges:
            from_stop = edge.getEdge('from_stop')['from_stop'].stopId
            to_stop = edge.getEdge('to_stop')['to_stop'].stopId
            distance = edge.getEdge('distance')['distance']

            self.neighbors[from_stop]['outgoing'].append([to_stop, distance, False])  # Outgoing edges
            self.neighbors[to_stop]['incoming'].append([from_stop, distance, False])  # Incoming edges
      # with open('./Output/Neighbors1.json', 'w') as file:
      #    json.dump(self.neighbors, file, ensure_ascii=False, indent=4)
      print("......Neighbors and costs built......")
      return self.neighbors
   
   def preImportance(self):
      for stop in self.stops:
         importance, _ = self.calculateShortcut(stop)
         heapq.heappush(self.q, (importance, stop))

      print(".......Importance calculated.......")
   
   def recalibrateNeighbors(self, stop):
      for prev, *_ in self.neighbors[stop]['incoming']:  # Incoming edges
         self.level[prev] = max(self.level[prev], self.level[stop] + 1)
      for next_,* _ in self.neighbors[stop]['outgoing']:  # Outgoing edges
         self.level[next_] = max(self.level[next_], self.level[stop] + 1)

   def computeNeighborsLevel(self, stop):
      num, level1, level2 = 0, 0, 0
      for prev, *_ in self.neighbors[stop]['incoming']:  # Incoming edges
         if self.rank[prev] != math.inf:
            num += 1
            level1 = max(level1, self.level[prev] + 1)
      for next_, *_ in self.neighbors[stop]['outgoing']:  # Outgoing edges
         if self.rank[next_] != math.inf:
            num += 1
            level2 = max(level2, self.level[next_] + 1)
      return num + (level1 + level2) / 2

   def witnessPath(self, source, contract, limit):
      heap = [(0, source)]
      dist_dict = {stop: math.inf for stop in self.stops}
      dist_dict[source] = 0

      while heap:
         dist, stop = heapq.heappop(heap)
         if dist >= limit:
            return dist_dict
         for to_stop, weight, _ in self.neighbors[stop]['outgoing']:  # Outgoing edges
            if self.rank[to_stop] < self.rank[contract] or contract == to_stop:
               continue
            if dist_dict[to_stop] > dist + weight:
               dist_dict[to_stop] = dist + weight
               heapq.heappush(heap, (dist_dict[to_stop], to_stop))

      return dist_dict

   def calculateShortcut(self, stop, adding_shortcuts=False):
      shortcut_count = 0
      shortcut_cover = set()
      shortcuts = []

      maxOutgoing = max([dist for _, dist, _ in self.neighbors[stop]['outgoing']], default=0) if len(self.neighbors[stop]['outgoing']) else 0
      minOutgoing = min([dist for _, dist, _ in self.neighbors[stop]['outgoing']], default=math.inf) if len(self.neighbors[stop]['outgoing']) else 0

      for prev, dist1, _ in self.neighbors[stop]['incoming']:  # Incoming edges
         if self.rank[prev] < self.rank[stop]:
            continue
         dist_dict = self.witnessPath(prev, stop, dist1 + maxOutgoing - minOutgoing)
         for next_, dist2, _ in self.neighbors[stop]['outgoing']:  # Outgoing edges
            if self.rank[next_] < self.rank[stop] or self.rank[prev] > self.rank[next_]:
               continue
            if dist1 + dist2 < dist_dict[next_]:
               shortcut_count += 1
               shortcut_cover.add(prev)
               shortcut_cover.add(next_)
               if adding_shortcuts:
                  shortcuts.append(Shortcut(to_stop=next_, from_stop=prev, distance=dist1 + dist2))
                  if prev not in self.contracted:
                     self.contracted[prev] = {}
                  self.contracted[prev][next_] = stop

               
      edge_diff = shortcut_count - len(self.neighbors[stop]['incoming']) - len(self.neighbors[stop]['outgoing'])

      importance = edge_diff + len(shortcut_cover) + self.computeNeighborsLevel(stop)
      return importance, shortcuts
   
   def addShortcut(self, from_stop, to_stop, dist):
      updated = False
      for i, (prev, weight, _) in enumerate(self.neighbors[to_stop]['incoming']):  # Incoming edges
         if prev == from_stop:
            self.neighbors[to_stop]['incoming'][i] = [prev, min(weight, dist), True]
            updated = True
            break

      if not updated:
         self.neighbors[to_stop]['incoming'].append([from_stop, dist, True])
         self.count += 1

      updated = False

      for i, (next_, weight, _) in enumerate(self.neighbors[from_stop]['outgoing']):  # Outgoing edges
         if next_ == to_stop:
            self.neighbors[from_stop]['outgoing'][i] = [next_, min(weight, dist), True]
            updated = True
            break

      if not updated:
         self.neighbors[from_stop]['outgoing'].append([to_stop, dist, True])
         self.count += 1

   def removeEdge(self):
      incoming_edges, outcoming_edges = 0, 0
      delete_edges = 0
      for stop in self.stops:
         for from_stop, dist, _ in self.neighbors[stop]['incoming']:  # Incoming edges
            if self.rank[from_stop] < self.rank[stop]:
               self.neighbors[stop]['incoming'].remove([from_stop, dist, _])
               delete_edges += 1

         for to_stop, dist, _ in self.neighbors[stop]['outgoing']:  # Outgoing edges
            if self.rank[to_stop] < self.rank[stop]:
               self.neighbors[stop]['outgoing'].remove([to_stop, dist, _])
               delete_edges += 1 
         incoming_edges += len(self.neighbors[stop]['incoming'])
         outcoming_edges += len(self.neighbors[stop]['outgoing'])
      
      print(f"Incoming edges: {incoming_edges}, Outcoming edges: {outcoming_edges}")
      print(f"Total shortcuts added: {self.count}")
      print(f"Total edges deleted: {delete_edges}")

   def preProcess(self):
      rank = 1
      start_time = datetime.now()
      self.preImportance()

      while self.q:
         stop = heapq.heappop(self.q)[1]
         try:
            next_stop = heapq.heappop(self.q)
            importance, shortcuts = self.calculateShortcut(stop, adding_shortcuts=True)
            if importance <= next_stop[0]:
               for shortcut in shortcuts:
                  self.addShortcut(shortcut.from_stop, shortcut.to_stop, shortcut.distance)
               self.rank[stop] = rank
               self.recalibrateNeighbors(stop)
            else:
               heapq.heappush(self.q, (importance, stop))

            rank += 1
            heapq.heappush(self.q, next_stop)
         except Exception as e:
            print(f"Exception at stop {stop}: {e}")
            self.rank[stop] = max(self.rank) + 1
      
      end_time = datetime.now()
      vertices = []
      for stop in range(self.n):
         if self.rank[stop] != math.inf:
            vertices.append(Vertex(stopId=stop, contraction_order=self.rank[stop], inward_edges=self.neighbors[stop]['incoming'], outward_edges=self.neighbors[stop]['outgoing']))
         else:
            vertices.append(Vertex(stop, -1, [], []))

      self.removeEdge()
      print(f"Time taken for preprocessing: {(end_time - start_time).total_seconds()} seconds")

      return vertices 

   def clearProcess(self):
     self.bidirect = [[math.inf] * self.n, [math.inf] * self.n]
     self.visited = [False] * self.n
     self.forwardPathTrace = {}
     self.backwardPathTrace = {} 

   def markVisited(self, stop):
      if not self.visited[stop]:
         self.visited[stop] = True
      
   def relaxingEdge(self, q, direction, stop, new_stop, dist, trace):
      if self.bidirect[direction][new_stop] > dist:
         self.bidirect[direction][new_stop] = dist
         heapq.heappush(q[direction], (self.bidirect[direction][new_stop], new_stop))
         trace[new_stop] = stop

   def runningEdge(self, q, direction, stop):
      if direction == 0:
         for to_stop, distance, _ in self.neighbors[stop]['outgoing']:  # Outgoing edges
            if self.rank[stop] > self.rank[to_stop]:
               continue
            self.relaxingEdge(q, direction, stop, to_stop, self.bidirect[direction][stop] + distance, self.forwardPathTrace)
      if direction == 1:
         for from_stop, distance, _ in self.neighbors[stop]['incoming']:  # Incoming edges
            if self.rank[from_stop] < self.rank[stop]:
               continue
            self.relaxingEdge(q, direction, stop, from_stop, self.bidirect[direction][stop] + distance, self.backwardPathTrace)

   def queryBidirectional(self, source, target):
      self.clearProcess()
      estimate = math.inf
      q = [[], []]

      self.relaxingEdge(q, 0, None, source, 0, self.forwardPathTrace)
      self.relaxingEdge(q, 1, None, target, 0, self.backwardPathTrace)
      self.markVisited(source)
      self.markVisited(target)
      # count = 2

      if source == target:
         return (0, 0, [])
      intersectStop = None
      
      start_time = datetime.now()
      while q[0] or q[1]:
         if q[0]:
            dist, stop = heapq.heappop(q[0])
            if self.bidirect[0][stop] <= estimate:
               self.runningEdge(q, 0, stop)
            
            if self.visited[stop] and self.bidirect[0][stop] + self.bidirect[1][stop] < estimate:
               estimate = self.bidirect[0][stop] + self.bidirect[1][stop]
               intersectStop = stop
            else:
               self.markVisited(stop)
               # count += 1

         if q[1]:
            dist, stop = heapq.heappop(q[1])
            if self.bidirect[1][stop] <= estimate:
               self.runningEdge(q, 1, stop)
            
            if self.visited[stop] and self.bidirect[0][stop] + self.bidirect[1][stop] < estimate:
               estimate = self.bidirect[0][stop] + self.bidirect[1][stop]
               intersectStop = stop

            else:
               self.markVisited(stop)
               # count += 1
      path = self.retrievePath(self.forwardPathTrace, self.backwardPathTrace, intersectStop)
      end_time = datetime.now()
      total_time = (end_time - start_time).total_seconds()
      return round(-1 if estimate == math.inf else estimate, 4), total_time, path
   
   def retrievePath(self, forwardPathTrace, backwardPathTrace, intersectStop):
      path = deque()
      # print(f"Intersection point: {intersectStop}")
      if intersectStop != None:
         path.append(intersectStop)
         current = intersectStop
         while forwardPathTrace and current in forwardPathTrace and forwardPathTrace[current]:
            current = forwardPathTrace[current]
            path.appendleft(current)

         current = intersectStop
         while backwardPathTrace and current in backwardPathTrace and backwardPathTrace[current]:
            current = backwardPathTrace[current]
            path.append(current)

      # expanding contraction edge
      expanded = False
      while not expanded:
         expanded = True
         e = 0
         while e < len(path) - 1:
            if path[e] in self.contracted and path[e+1] in self.contracted[path[e]]:
               contractedStop = self.contracted[path[e]][path[e+1]]
               path.insert(e+1, contractedStop)
               while contractedStop in self.contracted[path[e]]:
                  contractedStop = self.contracted[path[e]][contractedStop]
                  path.insert(e+1, contractedStop)
            e += 1

      # convert deque to list
      path = list(path)
      return path