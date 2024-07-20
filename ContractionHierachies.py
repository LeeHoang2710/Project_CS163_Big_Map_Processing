import heapq
import math
import json
from datetime import datetime

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
      self.neighbors = {}
      self.processing = []
      self.count = 0

   def buildNeighborsAndCosts(self):
      self.neighbors = {stop: {'incoming': [], 'outgoing': []} for stop in self.stops}
      for stop, edges in self.edges.items():
         for edge in edges:
            from_stop = edge.getEdge('from_stop')['from_stop'].stopId
            to_stop = edge.getEdge('to_stop')['to_stop'].stopId
            distance = edge.getEdge('distance')['distance']

            self.neighbors[from_stop]['outgoing'].append([to_stop, distance])
            self.neighbors[to_stop]['incoming'].append([from_stop, distance])

      # with(open('./Output/Neighbors.json', 'w')) as file:
      #    json.dump(self.neighbors, file, ensure_ascii=False, indent=4)
      # print("Neighbors file created")
      print("Neighbors and costs built")

      return self.neighbors
   
   
   def preImportance(self):
      for stop in self.stops:
         importance, _ = self.calculateShortcut(stop)
         heapq.heappush(self.q, (importance, stop))

      # with(open('./Output/PreImportance.json', 'w')) as file:
      #    json.dump(self.q, file, ensure_ascii=False, indent=4)
      # print("Importance file created")
      print("Importance calculated")
   
   def recalibrateNeighbors(self, stop):
      for prev, dist in self.neighbors[stop]['incoming']:
         self.level[prev] = max(self.level[prev], self.level[stop] + 1)
      for next_ , dist in self.neighbors[stop]['outgoing']:
         self.level[next_] = max(self.level[next_], self.level[stop] + 1)

   def computeNeighborsLevel(self, stop):
      num, level1, level2 = 0, 0, 0
      for prev, dist in self.neighbors[stop]['incoming']:
         if self.rank[prev] != math.inf:
            num += 1
            level1 = max(level1, self.level[prev] + 1)
      for next_, dist in self.neighbors[stop]['outgoing']:
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
         for to_stop, weight in self.neighbors[stop]['outgoing']:
            # Skip the already contracted stops
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

      maxOutgoing = max([dist for next_, dist in self.neighbors[stop]['outgoing']], default=0) if len(self.neighbors[stop]['outgoing']) else 0
      # maxIncoming = max([dist for prev, dist in self.neighbors[stop]['incoming']], default=0) if len(self.neighbors[stop]['incoming']) else 0
      minOutgoing = min([dist for prev, dist in self.neighbors[stop]['outgoing']], default=math.inf) if len(self.neighbors[stop]['outgoing']) else 0

      for prev, dist1 in self.neighbors[stop]['incoming']:
         # Skip the already contracted stops
         if self.rank[prev] < self.rank[stop]:
            continue
         dist_dict = self.witnessPath(prev, stop, dist1 + maxOutgoing - minOutgoing)
         for next_, dist2 in self.neighbors[stop]['outgoing']:
            # Skip the already contracted stops
            if self.rank[next_] < self.rank[stop] or self.rank[prev] > self.rank[next_]:
               continue
            if dist1 + dist2 < dist_dict[next_]:
               shortcut_count += 1
               shortcut_cover.add(prev)
               shortcut_cover.add(next_)
               if adding_shortcuts:
                  shortcuts.append(Shortcut(to_stop=next_, from_stop=prev, distance=dist1 + dist2))
               
      edge_diff = shortcut_count - len(self.neighbors[stop]['incoming']) - len(self.neighbors[stop]['outgoing'])

      importance = edge_diff + len(shortcut_cover) + self.computeNeighborsLevel(stop)
      return importance, shortcuts
   
   def addShortcut(self, from_stop, to_stop, dist):
      updated = False

      # Check if there is an existing incoming shortcut to 'to_stop' from 'from_stop'
      for i, (prev, weight) in enumerate(self.neighbors[to_stop]['incoming']):
         if prev == from_stop:
            # Update the distance if a shorter path is found
            self.neighbors[to_stop]['incoming'][i][1] = min(weight, dist)
            updated = True
            break

      # If no existing shortcut was updated, add a new one
      if not updated:
         self.neighbors[to_stop]['incoming'].append([from_stop, dist])
         self.count += 1

      # Reset flag for outgoing shortcut update
      updated = False

      # Check if there is an existing outgoing shortcut from 'from_stop' to 'to_stop'
      for i, (next_, weight) in enumerate(self.neighbors[from_stop]['outgoing']):
         if next_ == to_stop:
            # Update the distance if a shorter path is found
            self.neighbors[from_stop]['outgoing'][i][1] = min(weight, dist)
            updated = True
            break

      # If no existing shortcut was updated, add a new one
      if not updated:
         self.neighbors[from_stop]['outgoing'].append([to_stop, dist])
         self.count += 1

      

   def removeEdge(self):
      incoming_edges, outcoming_edges = 0, 0
      delete_edges = 0
      for stop in self.stops:
         for from_stop, distance in self.neighbors[stop]['incoming']:
            if self.rank[from_stop] < self.rank[stop]:
               self.neighbors[stop]['incoming'].remove([from_stop, distance])
               delete_edges += 1

         for to_stop, distance in self.neighbors[stop]['outgoing']:
            if self.rank[to_stop] < self.rank[stop]:
               self.neighbors[stop]['outgoing'].remove([to_stop, distance])
               delete_edges += 1 
         incoming_edges += len(self.neighbors[stop]['incoming'])
         outcoming_edges += len(self.neighbors[stop]['outgoing'])
      
      print(f"Incoming edges: {incoming_edges}, Outcoming edges: {outcoming_edges}")
      print(f"Total shortcuts added: {self.count}")
      print(f"Total edges deleted: {delete_edges}")

   def preProcess(self):
      """ Initialize the priority heap for stops importance
      Lazy update and contraction of stops in the graph """
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
            print("Exception:", e)
            self.rank[stop] = max(self.rank) + 1
      
      end_time = datetime.now()
      self.removeEdge()
      print(f"Time taken for preprocessing: {(end_time - start_time).total_seconds()} seconds")

   def clearProcess(self):
     self.bidirect = [[math.inf] * self.n, [math.inf] * self.n]
     self.visited = [False] * self.n
     self.processing = []

   def markVisited(self, stop):
      if not self.visited[stop]:
         self.visited[stop] = True
         self.processing.append(stop)
      
   def relaxingEdge(self, q, direction, stop, dist):
      """ Relax the distance to stop from direction side by value dist """
      # 0 for forward search, 1 for backward search
      if self.bidirect[direction][stop] > dist:
         self.bidirect[direction][stop] = dist
         heapq.heappush(q[direction], (self.bidirect[direction][stop], stop))

   def runningEdge(self, q, direction, stop):
      if direction == 0:
         for to_stop, distance in self.neighbors[stop]['outgoing']:
            # Go from lower rank to higher rank
            if self.rank[stop] > self.rank[to_stop]:
               continue
            self.relaxingEdge(q, direction, to_stop, self.bidirect[direction][stop] + distance)
      if direction == 1:
         for from_stop, distance in self.neighbors[stop]['incoming']:
            # Go from lower rank to higher rank
            if self.rank[from_stop] < self.rank[stop]:
               continue
            self.relaxingEdge(q, direction, from_stop, self.bidirect[direction][stop] + distance)

   def queryBidirectional(self, source, target):
      self.clearProcess()
      estimate = math.inf
      q = [[], []]

      self.relaxingEdge(q, 0, source, 0)
      self.relaxingEdge(q, 1, target, 0)
      self.markVisited(source)
      self.markVisited(target)

      if source == target:
         return 0
      
      start_time = datetime.now()
      while q[0] or q[1]:
         if q[0]:
            dist, stop = heapq.heappop(q[0])
            if self.bidirect[0][stop] <= estimate:
               self.runningEdge(q, 0, stop)
            
            if self.visited[stop] and self.bidirect[0][stop] + self.bidirect[1][stop] < estimate:
               estimate = self.bidirect[0][stop] + self.bidirect[1][stop]
            else:
               self.markVisited(stop)

         if q[1]:
            dist, stop = heapq.heappop(q[1])
            if self.bidirect[1][stop] <= estimate:
               self.runningEdge(q, 1, stop)
            
            if self.visited[stop] and self.bidirect[0][stop] + self.bidirect[1][stop] < estimate:
               estimate = self.bidirect[0][stop] + self.bidirect[1][stop]
            else:
               self.markVisited(stop)


      end_time = datetime.now()
      total_time = (end_time - start_time).total_seconds()
      # print(f"Time taken for bidirectional search: {(end_time - start_time).total_seconds()} seconds")
      return round(-1 if estimate == math.inf else estimate, 4), total_time
