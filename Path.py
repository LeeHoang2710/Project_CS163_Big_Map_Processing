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

    def readPathData(self, file_path):
        try:
            with open(file_path, mode='r') as file:
                data_list = [json.loads(line.strip()) for line in file]
                path_dict = {}
                result = []
                for data in data_list:  
                    lat_data = data["lat"]
                    lng_data = data["lng"]
                    route_id = data["RouteId"]
                    route_var_id = data["RouteVarId"]
                    # combine two lists of lat and lng into 1 list containing tuples
                    coordinate_data = [(lng, lat) for lat, lng in zip(lat_data, lng_data)]
                    path_obj = Path(Coordinates=coordinate_data, RouteId=route_id, RouteVarId=route_var_id)
                    path_dict.setdefault(route_id, {}).setdefault(route_var_id, [])
                    result.append(path_obj)
                    path_dict[route_id][route_var_id].append(path_obj)
                self.paths = result
                return path_dict
        except FileNotFoundError:
            raise FileNotFoundError("File not found:")    
         