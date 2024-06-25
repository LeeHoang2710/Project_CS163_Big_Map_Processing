import os
import json
import csv

class Stop():
   def __init__(self, StopId, Code, Name, StopType, Zone, Ward, AddressNo, Street, SupportDisability, Status, Lng, Lat, Search, Routes, RouteId, RouteVarId):
      self.stopId = StopId
      self.code = Code
      self.name = Name
      self.stopType = StopType
      self.zone = Zone
      self.ward = Ward
      self.address = AddressNo
      self.street = Street
      self.supportDisability = SupportDisability
      self.status = Status
      self.lng = Lng
      self.lat = Lat
      self.search = Search
      self.routes = Routes

      self.routeId = RouteId
      self.routeVarId = RouteVarId

   def getStop(self, *argv):
      result = {}
      allowed_properties = list(self.__dict__.keys())
      for arg in argv:
         if arg not in allowed_properties:
            raise ValueError(f"Invalid property {arg} in the property of Stop" + '\n' + f"Properties should look for {allowed_properties}")
         else:
            result[arg] = getattr(self, arg)
      return result
   
   def setStop(self, **kwargs):
      allowed_properties = list(self.__dict__.keys())
      for key, value in kwargs.items():
         if key not in allowed_properties:
            raise ValueError(f"Invalid property: {key}")
         else:
            setattr(self, key,value)
            print(f"Successfully changed {key} in Stop instance")

class StopQuery():
   def __init__(self):
      self.stops = []
   
   def searchByABC(self, **kwargs):
      datas = self.stops
      searchStop = []
      try:
         for data in datas:
            meet_all_conditions = True
            for key, value in kwargs.items():
               stop_dict = data.getStop(key)
               if stop_dict[key] != value:
                  meet_all_conditions = False
                  break
            if meet_all_conditions:
               searchStop.append(data)
         
         return searchStop
      except Exception as e:
         print(f"Error: {e}") 

   def outputAsCSV(self, query_list):
      home_dir = os.getcwd()
      filename = os.path.join(home_dir, "Output/Stop", "StopOutputAsCSV.csv")
      # query_list: [ [{}, {}] ,  [{} , {}] , ... ]
      try:
         with open(filename, newline='', mode='w', encoding='utf-8') as csvfile:
            fieldnames = ['stopId', 'code', 'name', 'stopType', 'zone', 'ward', 'address', 'street','supportDisability', 'status', 'lng', 'lat', 'search', 'routes', 'routeId', 'routeVarId']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            # write fieldnames to csv file
            writer.writeheader()
            for sublist in query_list:
               data = []
               for element in sublist:
                  data.append(element.getStop(*fieldnames))
               # write properties to csv file
               writer.writerows(data)
      except Exception as e:
         print(f"Error with CSV: {e}")

   def outputAsJSON(self, query_list):
      home_dir = os.getcwd()
      filename = os.path.join(home_dir, "Output/Stop", "StopOutputAsJSON.json")
      # query_list: [ [{}, {}] ,  [{} , {}] , ... ]
      try:
         with open(filename, mode='w', encoding='utf-8') as jsonfile:
             fieldnames = ['stopId', 'code', 'name', 'stopType', 'zone', 'ward', 'address', 'street','supportDisability', 'status', 'lng', 'lat', 'search', 'routes', 'routeId', 'routeVarId']
             all_data = []
             for sublist in query_list:
                for element in sublist:
                   all_data.append(element.getStop(*fieldnames))
             # convert python object into JSON-formatted string
             jsonfile.write(json.dumps(all_data,ensure_ascii=False) + '\n')
      except Exception as e:
         print(f"Error with JSON: {e}")

   def readStopData(self, file_path):
      try:
         with open(file_path, mode='r', newline="") as file:
            data_list = [json.loads(line.strip()) for line in file]
            data_stops = [data['Stops'] for data in data_list]
            result = []
            stop_dict = {}
            # enumerate: (0, seq[0]),(1, seq[1]),(2, seq[2]), ...
            for index, list_of_stops in enumerate(data_stops):
               route_id = data_list[index]["RouteId"]
               route_var_id = data_list[index]["RouteVarId"]
               # ensure the dictionary structure valid {[], [], ...}
               stop_dict.setdefault(route_id, {}).setdefault(route_var_id, [])
               for stop in list_of_stops:
                  stop_obj = Stop(**stop, RouteId=route_id, RouteVarId=route_var_id)
                  result.append(stop_obj)
                  stop_dict[route_id][route_var_id].append(stop_obj)
            self.stops = result
            return stop_dict
      except FileNotFoundError:
         raise FileNotFoundError("File not found:")