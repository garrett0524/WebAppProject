#A constructor that takes no parameters
import re
from util.request import Request


class Router:
    def __init__(self):
        self.routes = []  # List to store routes

    # A function that takes a Request object (from your util/request.py file) 
    # and returns a byte array (bytes) that will be the bytes of the response that will be sent to the client.

    #add route registers the route by storing each route and its related info in a dictionary
    def add_route(self,method,path,callback):
        self.routes.append({
            "method": method,
            "path": path,
            "callback": callback
        })

    #takes a request object, iterates throughs ored routes, checks if method and path amch the route, if match is found it calls handler function
    def route_request(self, request: Request) -> bytes:
        for route in self.routes:
            if route['method'] == request.method and re.match('^' + route['path'] + '$', request.path):
                return route['handler'](request) #call handler function\
            
        return b"HTTP/1.1 404 Not Found\r\n\r\n404 - Content not found" 

            
