import heapq
import math
import json
from datetime import datetime

class Vertex:
   def __init__(self, stopId, contraction_order, inward_edges, outward_edges):
      self.stopId = stopId
      self.contraction_order = contraction_order
      self.inward_edges = inward_edges
      self.outward_edges = outward_edges
      self.is_transit_node = False
      self.forward_search_space = {}
      self.forward_access_node_dist = {}
      self.forward_tnr_ed = False
      self.backward_search_space = {}
      self.backward_access_node_dist = {}
      self.backward_tnr_ed = False
      self.transit_path = {}
      self.voronoi_region_id = None
      self.dist = math.inf

class TNRGraph:
   def __init__(self, vertices, graph):
      self.vertices = vertices
      # Sort vertices by contraction_order in descending order
      self.sorted_vertices = sorted(vertices, key=lambda v: v.contraction_order, reverse=True)
      self.transit_nodes = []
      self.tnr_dist = {}
      self.contracted = False
      self.tnr_ed = False
      self.graph = graph
   

   def computeTNR(self, count):
      if not self.contracted:
         print('The graph has not been contracted, preprocess Contraction Hierachies first')
      if self.tnr_ed:
         print('The graph has already performed the Transit Node Routing')
      if count > len(self.vertices):
         print(f"Invalid amount of transit nodes. Maximum is: {len(self.vertices)}")

      start = datetime.now()
      self.selectTransitNodes(count)
      self.calculateDistanceTransitNode(count)
      self.markedVoronoiRegion()
      self.computeLocalityFilter()
      end = datetime.now()
      total_time = (end - start).total_seconds()
      print(f"Time taken for TNR: {total_time} seconds")

      self.tnr_ed = True

   def selectTransitNodes(self, count):    
    # Select the first (count) vertices as transit nodes
    for vertex in self.sorted_vertices[:count]:
        vertex.is_transit_node = True
        self.transit_nodes.append(vertex)
        # Create an empty dict for the transit path
        vertex.transit_path = {}

   def calculateDistanceTransitNode(self, count):
      for i in range(count):
         for j in range(count):
            if self.transit_nodes[i].stopId not in self.tnr_dist:
               self.tnr_dist[self.transit_nodes[i].stopId] = {}
            
            if i == j:
               self.tnr_dist[self.transit_nodes[i].stopId][self.transit_nodes[j].stopId] = 0
               continue

            distance, _, path = self.graph.queryBidirectional(source=self.transit_nodes[i].stopId, target=self.transit_nodes[j].stopId)
            self.tnr_dist[self.transit_nodes[i].stopId][self.transit_nodes[j].stopId] = distance

            # print(f"Transit path from {self.transit_nodes[i].stopId} to {self.transit_nodes[j].stopId}: {path}")
            for k in range(len(path) - 1):
               if self.transit_nodes[j].stopId in self.vertices[path[k]].transit_path:
                  break
               self.vertices[path[k]].transit_path[self.transit_nodes[j].stopId] = self.vertices[path[k + 1]]


   def markedVoronoiRegion(self):
      for vertex in self.vertices:
         vertex.dist = math.inf
         vertex.voronoi_region_id = -1

      dist_heap = []
      visited = set()

      for transitNode in self.transit_nodes:
         transitNode.dist = 0
         transitNode.voronoi_region_id = transitNode.stopId
         heapq.heappush(dist_heap, (transitNode.dist, transitNode.stopId))

      while dist_heap:
         dist, vertex = heapq.heappop(dist_heap)
         if vertex in visited:
            continue
         visited.add(vertex)
         for edge in self.vertices[vertex].inward_edges:
            # Check if edge is not a shortcut
            if not edge[2]:
               if self.vertices[vertex].dist + edge[1] < self.vertices[edge[0]].dist:
                  self.vertices[edge[0]].dist = self.vertices[vertex].dist + edge[1]
                  self.vertices[edge[0]].voronoi_region_id = self.vertices[vertex].voronoi_region_id
                  heapq.heappush(dist_heap, (self.vertices[edge[0]].dist, edge[0]))
   
   def computeLocalityFilter(self):
      contraction_max_heap = []
      for vertex in self.vertices:
         heapq.heappush(contraction_max_heap, (-vertex.contraction_order, vertex.stopId))

      while contraction_max_heap:
         _, source_vertex_id = heapq.heappop(contraction_max_heap)
         source_vertex = self.vertices[source_vertex_id]

         # Forward TNR computation
         if not source_vertex.forward_tnr_ed:
            source_vertex.forward_search_space = {}
            source_vertex.forward_access_node_dist = {}

            search_heap = []
            heapq.heappush(search_heap, (0, source_vertex.stopId))
            distance = {v.stopId: math.inf for v in self.vertices}
            distance[source_vertex.stopId] = 0

            while search_heap:
                  current_dist, query_vertex_id = heapq.heappop(search_heap)
                  query_vertex = self.vertices[query_vertex_id]

                  # Check if it's a transit node or not
                  if not query_vertex.is_transit_node:
                     source_vertex.forward_search_space[query_vertex.voronoi_region_id] = True

                     if self.vertices[query_vertex_id].forward_tnr_ed:
                        for i in self.vertices[query_vertex_id].forward_search_space:
                              source_vertex.forward_search_space[i] = True
                        for j in self.vertices[query_vertex_id].forward_access_node_dist:
                              source_vertex.forward_access_node_dist[j] = -1
                     else:
                        for edge in query_vertex.outward_edges:
                              # neighbor = self.vertices[edge[0]]
                              if source_vertex.contraction_order < self.vertices[edge[0]].contraction_order:
                                 new_dist = current_dist + edge[1]
                                 if new_dist < distance[self.vertices[edge[0]].stopId]:
                                    distance[self.vertices[edge[0]].stopId] = new_dist
                                    heapq.heappush(search_heap, (new_dist, self.vertices[edge[0]].stopId))
                  else:
                     source_vertex.forward_access_node_dist[query_vertex.stopId] = -1

            for k in source_vertex.forward_access_node_dist:
                  source_vertex.forward_access_node_dist[k] = self.graph.queryBidirectional(source_vertex.stopId, k)[0]

            # Filter out redundant access nodes
            access_node_mask = {}
            for a, a1 in source_vertex.forward_access_node_dist.items():
                  for b, b1 in source_vertex.forward_access_node_dist.items():
                     if a == b:
                        continue
                     if a1 + self.tnr_dist[a][b] <= b1:
                        access_node_mask[b] = True

            for h in access_node_mask:
                  del source_vertex.forward_access_node_dist[h]

            source_vertex.forward_tnr_ed = True

         # Backward TNR computation
         if not source_vertex.backward_tnr_ed:
            source_vertex.backward_search_space = {}
            source_vertex.backward_access_node_dist = {}

            search_heap = []
            heapq.heappush(search_heap, (0, source_vertex.stopId))
            distance = {v.stopId: math.inf for v in self.vertices}
            distance[source_vertex.stopId] = 0

            while search_heap:
                  current_dist, query_vertex_id = heapq.heappop(search_heap)
                  query_vertex = self.vertices[query_vertex_id]

                  # Check if it's a transit node
                  if not query_vertex.is_transit_node:
                     source_vertex.backward_search_space[query_vertex.voronoi_region_id] = True

                     if self.vertices[query_vertex_id].backward_tnr_ed:
                        for i in self.vertices[query_vertex_id].backward_search_space:
                              source_vertex.backward_search_space[i] = True
                        for j in self.vertices[query_vertex_id].backward_access_node_dist:
                              source_vertex.backward_access_node_dist[j] = -1
                     else:
                        for edge in query_vertex.inward_edges:
                              # neighbor = self.vertices[edge[0]]
                              if source_vertex.contraction_order < self.vertices[edge[0]].contraction_order:
                                 new_dist = current_dist + edge[1]
                                 if new_dist < distance[self.vertices[edge[0]].stopId]:
                                    distance[self.vertices[edge[0]].stopId] = new_dist
                                    heapq.heappush(search_heap, (new_dist, self.vertices[edge[0]].stopId))
                  else:
                     source_vertex.backward_access_node_dist[query_vertex.stopId] = -1

            for k in source_vertex.backward_access_node_dist:
                  source_vertex.backward_access_node_dist[k] = self.graph.queryBidirectional(k, source_vertex.stopId)[0]

            # Filter out redundant access nodes
            access_node_mask = {}
            for a, a1 in source_vertex.backward_access_node_dist.items():
                  for b, b1 in source_vertex.backward_access_node_dist.items():
                     if a == b:
                        continue
                     if a1 + self.tnr_dist[b][a] <= b1:
                        access_node_mask[b] = True

            for h in access_node_mask:
                  del source_vertex.backward_access_node_dist[h]

            source_vertex.backward_tnr_ed = True

   def queryWithTNR(self, source, target):
      if not self.tnr_ed:
         print('The graph has not performed the Transit Node Routing')
         return None
      if source == target:
         return 0
      
      source_vertex = self.vertices[source]
      target_vertex = self.vertices[target]

      start = datetime.now()

      # check if there are access nodes
      if len(source_vertex.forward_access_node_dist) == 0 or len(target_vertex.backward_access_node_dist) == 0:
         print('Fallback to Contraction Hierachies because there are no access nodes')
         return self.graph.queryBidirectional(source, target)[0]
      
      # check if the source and target are in the same voronoi region (local search)
      for k in source_vertex.forward_search_space:
         if k in target_vertex.backward_search_space:
            print("Fallback to Contraction Hierachies because local search")
            return self.graph.queryBidirectional(source, target)[0]
         
      bestDist = math.inf
      bestSourceAccessNode = None
      bestTargetAccessNode = None

      for a, a1 in source_vertex.forward_access_node_dist.items():
         for b, b1 in target_vertex.backward_access_node_dist.items():
            # two transit nodes are not reachable
            if bestDist > a1 + self.tnr_dist[a][b] + b1:
               bestDist = a1 + self.tnr_dist[a][b] + b1
               bestSourceAccessNode = a
               bestTargetAccessNode = b

      path = self.constructPath(source, target, bestSourceAccessNode, bestTargetAccessNode)
      end = datetime.now()
      total_time = (end - start).total_seconds()
      print(f"Time taken for TNR query: {total_time} seconds")

      return bestDist, path
   

   def constructPath(self, source, target, bestSourceAccessNode, bestTargetAccessNode):
       forward = [math.inf] * len(self.vertices)
       backward = [math.inf] * len(self.vertices)
       forward[source] = 0
       backward[target] = 0

       forwardSearchHeap = []
       forwardPathTrace = {}
       heapq.heappush(forwardSearchHeap, (0, source))
      
       while forwardSearchHeap:
         dist, curr = heapq.heappop(forwardSearchHeap)
         if dist != math.inf:
             if curr == bestSourceAccessNode:
                 break
             for outEdge in self.vertices[curr].outward_edges:
                 if self.vertices[curr].contraction_order < self.vertices[outEdge[0]].contraction_order:
                     newDist = outEdge[1] + forward[curr]
                     if newDist < forward[outEdge[0]]:
                         forward[outEdge[0]] = newDist
                         forwardPathTrace[outEdge[0]] = curr
                         heapq.heappush(forwardSearchHeap, (newDist, outEdge[0]))

       backwardSearchHeap = []
       backwardPathTrace = {}
       heapq.heappush(backwardSearchHeap, (0, target))

       while backwardSearchHeap:
           dist, curr = heapq.heappop(backwardSearchHeap)
           if dist != math.inf:
               if curr == bestTargetAccessNode:
                   break
               for inEdge in self.vertices[curr].inward_edges:
                   if self.vertices[curr].contraction_order < self.vertices[inEdge[0]].contraction_order:
                       newDist = inEdge[1] + backward[curr]
                       if newDist < backward[inEdge[0]]:
                           backward[inEdge[0]] = newDist
                           backwardPathTrace[inEdge[0]] = curr
                           heapq.heappush(backwardSearchHeap, (newDist, inEdge[0]))

       fromSource = self.graph.retrievePath(forwardPathTrace, None, bestSourceAccessNode)
       fromTarget = self.graph.retrievePath(None, backwardPathTrace, bestTargetAccessNode)

       pathBetweenAccessNodes = []
       currentNode = self.vertices[bestSourceAccessNode]
       while currentNode != self.vertices[bestTargetAccessNode] and currentNode.transit_path[bestTargetAccessNode] is not None:
           pathBetweenAccessNodes.append(currentNode.stopId)
           currentNode = currentNode.transit_path[bestTargetAccessNode]

       path = fromSource[:-1] + pathBetweenAccessNodes + fromTarget

       return path