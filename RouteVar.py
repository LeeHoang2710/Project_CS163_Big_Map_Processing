import os
import json
import csv

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
      


#route = RouteVar(3, 5,"Lượt đi: Bến Thành - Thạnh Lộc","Thạnh Lộc", "03","Bến xe buýt Sài Gòn","THẠNH LỘC",21456,True,70)
#attribute = route.getRouteVar('routeId', 'endStop', 'routeVarShort')
#update = route.setRouteVar(distance=15.0, runningTime=50)
#print(attribute)
#print(f"Updated distance: {route.distance}")
#print(f"Updated running time: {route.runningTime}")

class RouteVarQuery:
    # this class is a list of route vars
   def __init__(self):
      self.route_vars = []
   # return data type: [[object1 , object2],[object1 , object2], ...]
   def searchByABC(self, **kwargs):
      datas = self.route_vars
      result = []
      try:
         for data in datas:
           meet_all_conditions = True
           for key, value in kwargs.items():
              # retrieve the specific properties for this key
              route_var_dict = data.getRouteVar(key)
              print(route_var_dict)
              # check if the value for this key matches the expected values
              if route_var_dict[key] != value:
                 meet_all_conditions = False
                 break
                 # no need to check further conditions for this data
           if meet_all_conditions:
               result.append(data)
         return result
      except Exception as e:
         print(f"Error: {e}")    

   def outputAsCSV(self, query_list):
      home_dir = os.getcwd()
      filename = os.path.join(home_dir, "Output/Route", "RouteVarOutputAsCSV.csv")
      # query_list: [ [{}, {}] ,  [{} , {}] , ... ]
      try:
         with open(filename, newline='', mode='w', encoding='utf-8') as csvfile:
            fieldnames = ['routeId', 'routeVarId', 'routeVarName', 'routeVarShort', 'routeNo', 'startStop', 'endStop', 'distance', 'outbound', 'runningTime']
            # create a writer csv method
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            # write fieldnames to csv file
            writer.writeheader()
            for sublist in query_list:
               data = []
               for element in sublist:
                  data.append(element.getRouteVar(*fieldnames))
               # write properties to csv file
               writer.writerows(data)
      except Exception as e:
         print(f"Error with CSV: {e}")

   def outputAsJSON(self, query_list):
      home_dir = os.getcwd()
      filename = os.path.join(home_dir, "Output/Route", "RouteVarOutputAsJSON.json")
      # query_list: [ [{}, {}] ,  [{} , {}] , ... ]
      try:
         with open(filename, mode='w', encoding='utf-8') as jsonfile:
             fieldnames = ['routeId', 'routeVarId', 'routeVarName', 'routeVarShort', 'routeNo', 'startStop', 'endStop', 'distance', 'outbound', 'runningTime']
             all_data = []
             for sublist in query_list:
                for element in sublist:
                   all_data.append(element.getRouteVar(*fieldnames))
             # convert python object into JSON-formatted string
             jsonfile.write(json.dumps(all_data,ensure_ascii=False) + '\n')
      except Exception as e:
         print(f"Error with JSON: {e}")

route1 = RouteVar(1, 101, "Route 1", "R1", "01", "Start 1", "End 1", 10.0, True, 30)
route2 = RouteVar(2, 102, "Route 2", "R2", "02", "Start 2", "End 2", 20.0, False, 40)
route3 = RouteVar(3, 103, "Route 3", "R3", "03", "Start 3", "End 3", 15.0, True, 35)
# add instances to RouteVarQuery
query = RouteVarQuery()
query.route_vars.append(route1)
query.route_vars.append(route2)
query.route_vars.append(route3)
# query.outputAsCSV([query.route_vars])
query.outputAsJSON([query.route_vars])
# use search function to find route
# matching_routes = query.searchByABC(outbound=True, routeId=1)
# if matching_routes == []: 
#    print("No routes found")
# for route in matching_routes:
#     print(f"Route ID: {route.routeId}, Route Name: {route.routeVarName}, Running Time: {route.runningTime}")

