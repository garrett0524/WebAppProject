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
            # if request.path == "/upload-pic":
            #     print("method",route['method'])
            #     print("path",route["path"])
            #     print("my method",request.method)
            #     print("my path",request.path)
            if route['method'] == request.method and re.match('^' + route['path'] , request.path):
                return route['callback'](request) #call callback function\
    
        return b"HTTP/1.1 404 Not Found\r\n\r\n404 - Content not found" 


def test_upload_pic():
    def handle_upload_pic(r):
        print("i was called")
    router = Router()
    router.add_route('POST', '^/upload-pic$', handle_upload_pic)

    

    request = Request(b'POST /upload-pic HTTP/1.1\r\nHost: localhost:8080\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\nSec-Fetch-Site: same-origin\r\nAccept-Language: en-US,en;q=0.9\r\nAccept-Encoding: gzip, deflate\r\nSec-Fetch-Mode: navigate\r\nContent-Type: multipart/form-data; boundary=----WebKitFormBoundaryHWsspClnN7YZEd4C\r\nOrigin: http://localhost:8080\r\nUser-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3.1 Safari/605.1.15\r\nReferer: http://localhost:8080/\r\nUpgrade-Insecure-Requests: 1\r\nContent-Length: 1033613\r\nConnection: keep-alive\r\nSec-Fetch-Dest: document\r\nCookie: visits=101; auth_token=iMGDE62RoKfellLyazMlfoLfqiK17fLYvmB39X2Fa8I\r\n\r\n------WebKitFormBoundaryHWsspClnN7YZEd4C\r\nContent-Disposition: form-data; name="image"; filename="Sample-jpg-image-1mb.jpg"\r\nContent-Type: image/jpeg\r\n\r\n\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xe1\x12\x14Exif\x00\x00MM\x00*\x00\x00\x00\x08\x00\x0b\x01\x0f\x00\x02\x00\x00\x00\x06\x00\x00\x00\x92\x01\x10\x00\x02\x00\x00\x00\n\x00\x00\x00\x98\x01\x12\x00\x03\x00\x00\x00\x01\x00\x01\x00\x00\x01\x1a\x00\x05\x00\x00\x00\x01\x00\x00\x00\xa2\x01\x1b\x00\x05\x00\x00\x00\x01\x00\x00\x00\xaa\x01(\x00\x03\x00\x00\x00\x01\x00\x02\x00\x00\x011\x00\x02\x00\x00\x00\x07\x00\x00\x00\xb2\x012\x00\x02\x00\x00\x00\x14\x00\x00\x00\xba\x02\x13\x00\x03\x00\x00\x00\x01\x00\x01\x00\x00\x87i\x00\x04\x00\x00\x00\x01\x00\x00\x00\xce\x88%\x00\x04\x00\x00\x00\x01\x00\x00\x06N\x00\x00\x07\x86Apple\x00iPhone 6s\x00\x00\x00\x00H\x00\x00\x00\x01\x00\x00\x00H\x00\x00\x00\x0110.1.1\x00\x002016:12:02 11:10:20\x00\x00!\x82\x9a\x00\x05\x00\x00\x00\x01\x00\x00\x02`\x82\x9d\x00\x05\x00\x00\x00\x01\x00\x00\x02h\x88"\x00\x03\x00\x00\x00\x01\x00\x02\x00\x00\x88\'\x00\x03\x00\x00\x00\x01\x00\x19\x00\x00\x90\x00\x00\x07\x00\x00\x00\x040221\x90\x03\x00\x02\x00\x00\x00\x14\x00\x00\x02p\x90\x04\x00\x02\x00\x00\x00\x14\x00\x00\x02\x84\x91\x01\x00\x07\x00\x00\x00\x04\x01\x02\x03\x00\x92\x01\x00\n\x00\x00\x00\x01\x00\x00\x02\x98\x92\x02\x00\x05\x00\x00\x00\x01\x00\x00\x02\xa0\x92\x03\x00\n\x00\x00\x00\x01\x00\x00\x02\xa8\x92\x04\x00\n\x00\x00\x00\x01\x00\x00\x02\xb0\x92\x07\x00\x03\x00\x00\x00\x01\x00\x05\x00\x00\x92\t\x00\x03\x00\x00\x00\x01\x00\x18\x00\x00\x92\n\x00\x05\x00\x00\x00\x01\x00\x00\x02\xb8\x92\x14\x00\x03\x00\x00\x00\x04\x00\x00\x02\xc0\x92|\x00\x07\x00\x00\x03:\x00\x00\x02\xc8\x92\x91\x00\x02\x00\x00\x00\x04955\x00\x92\x92\x00\x02\x00\x00\x00\x04955\x00\xa0\x00\x00\x07\x00\x00\x00\x040100\xa0\x01\x00\x03\x00\x00\x00\x01\x00\x01\x00\x00\xa0\x02\x00\x04\x00\x00\x00\x01\x00\x00\x0f\xc0\xa0\x03\x00\x04\x00\x00\x00\x01\x00\x00\x0b\xd0\xa2\x17\x00\x03\x00\x00\x00\x01\x00\x02\x00\x00\xa3\x01\x00\x07\x00\x00\x00\x01\x01\x00\x00\x00\xa4\x02\x00\x03\x00\x00\x00\x01\x00\x00\x00\x00\xa4\x03\x00\x03\x00\x00\x00\x01\x00\x00\x00\x00\xa4\x05\x00\x03\x00\x00\x00\x01\x00\x1d\x00\x00\xa4\x06\x00\x03\x00\x00\x00\x01\x00\x00\x00\x00\xa42\x00\x05\x00\x00\x00\x04\x00\x00\x06\x02\xa43\x00\x02\x00\x00\x00\x06\x00\x00\x06"\xa44\x00\x02\x00\x00\x00#\x00\x00\x06(\xea\x1d\x00\t\x00\x00\x00\x01\x00\x00\x00\x0c\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x10\xb2\x00\x00\x00\x0b\x00\x00\x00\x052016:12:02 11:10:20\x002016:12:02 11:10:20\x00\x00\x00-k\x00\x00\x03\xc4\x00\x00\x1f/\x00\x00\r\xb5\x00\x00G\xea\x00\x00\x05\xe3\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00S\x00\x00\x00\x14\x07\xdf\x05\xe7\x08\xa9\x052Apple iOS\x00\x00\x01MM\x00\n\x00\x01\x00\t\x00\x00\x00\x01\x00\x00\x00\x04\x00\x02\x00\x07\x00\x00\x02.\x00\x00\x00\x8c\x00\x03\x00\x07\x00\x00\x00h\x00\x00\x02\xba\x00\x04\x00\t\x00\x00\x00\x01\x00\x00\x00\x01\x00\x05\x00\t\x00\x00\x00\x01\x00\x00\x00\xed\x00\x06\x00\t\x00\x00\x00\x01\x00\x00\x00\xe8\x00\x07\x00\t\x00\x00\x00\x01\x00\x00\x00\x01\x00\x08\x00\n\x00\x00\x00\x03\x00\x00\x03"\x00\x0e\x00\t\x00\x00\x00\x01\x00\x00\x00\x00\x00\x14\x00\t\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00bplist00O\x11\x02\x00\xa6\x00\x9a\x00\x94\x00\x99\x00\xa2\x00\xbc\x00\xf7\x00P\x01\x8a\x02:\x03\xf8\x01"\x01\x00\x01\xce\x00L\x00,\x00\x9d\x00\x94\x00\x90\x00\x95\x00\xa3\x00\xc5\x00\t\x01h\x01B\x02\xa7\x01%\x01\xf9\x00\xda\x00\xbe\x00\xa2\x00)\x00\x91\x00\x8b\x00\x8c\x00\x93\x00\xa4\x00\xcd\x00\x1d\x01\x80\x01\x89\x01\x06\x01\xe5\x00\xd1\x00\xc4\x00\xbd\x00\xfd\x00r\x00\x88\x00\x85\x00\x87\x00\x91\x00\xa7\x00\xd7\x001\x01j\x01,\x01\xce\x00\xc0\x00\xb8\x00\x89\x00\xa9\x00\x04\x01\xe5\x00\x80\x00\x83\x00\x85\x00\x93\x00\xab\x00\xe3\x00B\x01"\x01\xe1\x00\xaf\x00\xaf\x00\xb5\x00t\x00\xad\x00\x08\x01\x16\x01x\x00|\x00\x81\x00\x91\x00\xb0\x00\xf1\x008\x01\xe0\x00\xa9\x00\xa1\x00\x95\x00\xf0\x00y\x00\xb9\x00\x0f\x01\x1f\x01t\x00v\x00\x80\x00\x92\x00\xb7\x00\x03\x01\x15\x01\xba\x00\xa3\x00\xee\x00\x97\x00\x0e\x01\x7f\x00\xcf\x00\x1b\x01&\x01r\x00t\x00\x7f\x00\x93\x00\xbf\x00\x16\x01\xde\x00\xa9\x00\xf2\x00[\x01\xba\x006\x01\x85\x00\xf4\x00(\x01\'\x01n\x00s\x00\x7f\x00\x98\x00\xc9\x00\x11\x01\xbb\x00\x9f\x00L\x01u\x01\xed\x00K\x01\x88\x00\x1c\x01+\x01)\x01n\x00t\x00\x80\x00\x9d')
    response_bytes = router.route_request(request)


# def test_basic_route_matching():
#         router = Router()

#         def callback(request):
#             return b"Test Response"

#         router.add_route('GET', '^/$', callback)
#         router.add_route('POST', '^/users$', callback)

#         #  GET request to /
#         request_get = Request(b"GET / HTTP/1.1\r\n\r\n")
#         response_get = router.route_request(request_get)
#         assert(response_get == b"Test Response")

#         #  POST request to /users
#         request_post = Request(b"POST /users HTTP/1.1\r\n\r\n")
#         response_post = router.route_request(request_post)
#         assert(response_post == b"Test Response")

#         #  non-matching request
#         request_invalid = Request(b"GET /invalid HTTP/1.1\r\n\r\n")
#         response_invalid = router.route_request(request_invalid)
#         assert(response_invalid == None)


if __name__ == '__main__':
    test_upload_pic()
#     test_basic_route_matching()