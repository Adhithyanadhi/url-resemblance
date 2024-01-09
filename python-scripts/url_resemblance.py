import logging
import os
import sys

from typing import List

# CWD = os.getcwd()
ROUTE_ID = 0

def get_next_route_id() -> int:
    global ROUTE_ID
    ROUTE_ID += 1
    return ROUTE_ID

class Route():
    def __init__(self, line_num, type, method, path_variable_count, path_variables):
        self.line_num = line_num
        self.type = type
        self.method: str = method
        if len(path_variables) != path_variable_count:
            raise Exception(f"invalid url properties path variable count {path_variable_count} and path_variables {path_variables}")
        self.route_id = get_next_route_id()
        self.path_variable_count: int = path_variable_count
        self.path_variables: List[str] = [x for x in path_variables]
    def __repr__(self):
        return str(vars(self))

METHOD_MAP = {
    "get": "GET",
    "http.methodget": "GET",
    "http.methodpost": "POST",
    "http.methodput": "PUT",
    "http.methoddelete": "DELETE",
    "http.methodpatch": "PATCH",
}

ROUTES_MAP = {
    "public":{
        "GET": [],
        "POST": [],
        "PATCH": [],
        "PUT": [],
        "DELETE": [],
    },
    "private":{
        "GET": [],
        "POST": [],
        "PATCH": [],
        "PUT": [],
        "DELETE": [],
    },
    "api":{
        "GET": [],
        "POST": [],
        "PATCH": [],
        "PUT": [],
        "DELETE": [],
    },
}

def get_method(method):
    if METHOD_MAP.get(method.strip().lower()) is None:
        return None
    return METHOD_MAP.get(method.strip().lower())

def read_file_contents(path: str) -> str:
    if not path:
        logging.error(f"File path cannot be empty {path}", exc_info  =  True)
        raise Exception(f"File path cannot be empty {path}")
    file  =  open(path, "r")
    file_contents  =  file.read()
    file.close()
    return file_contents

def get_matching_routes(r: Route) -> bool:
    routes: List[Route] = ROUTES_MAP[r.type][r.method]
    matching_routes : List[Route] = []
    for route in routes:
        if route.route_id > r.route_id:
            continue
        if route.path_variable_count != r.path_variable_count:
            continue
        match_count: int = 0
        for i in range(r.path_variable_count):
            if route.path_variables[i] == r.path_variables[i]:
                match_count += 1
            elif route.path_variables[i] == "::any::":
                match_count += 1
            else:
                break
        if match_count == r.path_variable_count:
            matching_routes.append(route)
    return matching_routes

def form_route(line_num: int, route, type):
    route_info: List[str] = route.split(',')
    method, url_path = get_method(route_info[1].replace('"', '').replace('\'', '')), route_info[2].replace('"', '').replace('\'', '')
    if method == None:
        pass
    path_variables = []
    url_path_variables = url_path.split('/')
    for path_variable in url_path_variables:
        if path_variable[0] == '{' and path_variable[-1] == '}':
            path_variable = "::any::"
        path_variables.append(path_variable)
    return Route(line_num=line_num, type=type, method=method, path_variable_count=len(path_variables)-1, path_variables=path_variables[1:])
    
    

def main():
    try: 
        routes_file_path = sys.argv[1]
        routes_file_contents: str = read_file_contents(path = routes_file_path)
        routes_file_contents = routes_file_contents.split('\n')
        routes = []
        for i in range(len(routes_file_contents)):
            route = routes_file_contents[i].strip()
            if route.startswith("server."):
                if "constants.PublicURLSlug" in route:
                    r = form_route(i, route, "public")
                    routes.append(r)
                    ROUTES_MAP["public"][r.method].append(r)
                elif "constants.PrivateURLSlug" in route:
                    r = form_route(i, route, "private")
                    routes.append(r)
                    ROUTES_MAP["private"][r.method].append(r)
                elif "constants.ApiURLSlug" in route:
                    r = form_route(i, route, "api")
                    routes.append(r)
                    ROUTES_MAP["api"][r.method].append(r)
                elif "/ping" in route or "server.Start" in route:
                    continue
                else:
                    raise Exception(f"unhanlded: route: {route}")
        
        for i in range(len(routes)):
            route = routes[i]
            matching_routes: List[Route] = get_matching_routes(route)
            if len(matching_routes) != 1:
                duplicate_routes_line_number = []
                for matching_route in matching_routes:
                    duplicate_routes_line_number.append(str(matching_route.line_num))
                print(f"route matched in line number {','.join(duplicate_routes_line_number)} found")
    except Exception as e:
        print(e)
if __name__ == "__main__":
    main()
    print("exited")