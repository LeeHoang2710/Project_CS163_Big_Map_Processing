import json
import os

class Path():
   def __init__(self, Coordinates, RouteId, RouteVarId):
      self.coordinates = Coordinates
      # coordinates include lat and lng 
      self.routeId = RouteId
      self.routeVarId = RouteVarId

   def getPath(self, *argv):
        result = {}
        allowed_properties = list(self.__dict__.keys())
        for arg in argv:
            if arg not in allowed_properties:
                raise ValueError(f"Invalid property {arg} in the property of Stop" + '\n' + f"Properties should look for {allowed_properties}")
        for arg in argv:
            result[arg] = getattr(self, arg)
        return result
   
   def setRouteVar(self, **kwargs):
        allowed_properties = list(self.__dict__.keys())
        for key, value in kwargs.items():
            if key not in allowed_properties:
                raise ValueError(f"Invalid property: {key}")
            else:
               setattr(self, key, value)
               print(f"Successfully changed {key} in Path instance")
                    
class PathQuery():
    def __init__(self):
        self.paths = []

    def searchByABC(self, **kwargs):
        datas = self.paths
        searchPath = []
        try:
            for data in datas:
                meet_all_conditions = True
                for key, value in kwargs.items():
                    path_dict = data.getPath(key)
                    if path_dict[key] != value:
                        meet_all_conditions = False
                        break
                if meet_all_conditions:
                    searchPath.append(data)
            return searchPath
        except Exception as e:
            print(f"Error: {e}")

    def outputAsJSON(self, query_list):
        home_dir = os.getcwd()
        filename = os.path.join(home_dir, "Output/Path", "PathOutputAsJSON.json")
        try:
            with open(filename, mode='w', encoding='utf-8') as jsonfile:
                fieldnames = ['coordinates', 'routeId', 'routeVarId']
                all_data = []
                for sublist in query_list:
                    for element in sublist:
                        all_data.append(element.getPath(*fieldnames))
                jsonfile.write(json.dump(all_data, ensure_ascii=False) + '\n')
        except Exception as e:
            print(f"Error with JSON: {e}")        
            
         