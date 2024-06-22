import os
import json

class RouteVar():
   def __init__(self, RouteId, RouteVarId, RouteVarName, RouteVarShortName, RouteNo, StartStop, EndStop, Distance, Outbound, RunningTime):
      self.routeId = RouteId
      self.routeVarId = RouteVarId
      self.routeVarName = RouteVarName
      self.routeVarShort = RouteVarShortName
      self.routeNo = RouteNo
      self.startStop = StartStop
      self.endStop = EndStop
      self.distance = Distance
      self.outbound = Outbound
      self.runningTime = RunningTime

   # retrieve specific properties of an instance of a class and return them in a dictionary. We pass a variable number of arguments(*argv) --> represent the names of the properties to retrieve. 
   def getRouteVar(self, *argv):
      result = {}
      # [routeId, routeVarName, routeNo, ...]
      allowed_properties = list(self.__dict__.keys())
      for arg in argv:
         if arg not in allowed_properties:
            raise ValueError(f"Invalid property {arg} in the property of RouteVar" + '\n' + f"Properties should look for {allowed_properties}")
         else:
            result[arg] = getattr(self, arg)
      return result

   def setRouteVar(self, **kwargs):
      allowed_propeties = list(self.__dict__.keys())
      for key, value in kwargs.items():
         if key not in allowed_propeties:
            raise ValueError(f"Invalid propeties {key}")
         else:
            setattr(self, key, value)
            print(f"Successfully changed {key} in RouteVar instance")
      return True




route = RouteVar(3, 5,"Lượt đi: Bến Thành - Thạnh Lộc","Thạnh Lộc", "03","Bến xe buýt Sài Gòn","THẠNH LỘC",21456.000000000007,True,70)
attribute = route.getRouteVar('routeId', 'endStop', 'routeVarShort')
update = route.setRouteVar(distance=15.0, runningTime=50)
print(attribute)
print(f"Updated distance: {route.distance}")
print(f"Updated running time: {route.runningTime}")