import html
import json
import socketserver
from util.request import Request
from util.router import router
import pymongo

myclient = pymongo.MongoClient("mongo:27017")
db = myclient["mydatabase"]
chat_collection = db["chat"]

class MyTCPHandler(socketserver.BaseRequestHandler):
    #set visit count var in class
    visit_count = 0
    message_id = 0

    def parse_cookies(self, headers):
        cookies = {}
        for header_name, header_value in headers.items():
            if header_name.lower() == "cookie":
                cookie_str = header_value.strip()
                for cookie in cookie_str.split(";"):
                    key, value = cookie.split("=")
                    cookies[key.strip()] = value.strip()
        return cookies

    
    def handle(self):
        received_data = self.request.recv(2048)
        print(self.client_address)
        print("--- received data ---")
        print(received_data)
        print("--- end of data ---\n\n")
        request = Request(received_data)

        #set path equal to the request path
        path = request.path 
        
        #default content type of empty str
        content_type = ""


        #dictionary for paths to set content type 
        if ".txt" in path:
            content_type = "text/plain"

        elif ".html" in path:
            content_type = "text/html"

        elif ".css" in path:
            content_type = "text/css"
        elif ".js" in path:
            content_type = "text/javascript"
        elif ".png" in path:
            content_type = "image/png"
        elif ".ico" in path:
            content_type = "image/x-icon"

        elif ".jpg" in path or ".jpeg" in path:
            content_type = "image/jpeg"

        elif ".mp4" in path:
            content_type = "video/mp4"
        elif ".json" in path:
            content_type = "application/json"

        #parse req headers to get cookies
        cookies = self.parse_cookies(request.headers)
        #print("request.headers"+str(request.headers))
        #print("cookies:"+str(cookies))

        if "visits" in cookies:
            MyTCPHandler.visit_count = int(cookies["visits"])
            #if visits isnt in cookies, set value to 1
        else:
            MyTCPHandler.visit_count = 0


        #if path equals "/" set path to index.html, set content type to text/html, increment cookie count, replace visit count in html file
        if path == "/":
            path = "public/index.html"
            content_type = "text/html"
            MyTCPHandler.visit_count +=1


            try:
                with open(path, "rb") as html_file:
                    html_content = html_file.read().decode("utf-8")
            except FileNotFoundError:
                # File not found, respond with a 404 status and a plain text message
                not_found_response = (
                    "HTTP/1.1 404 Not Found\r\n"
                    "Content-Type: text/plain; charset=utf-8\r\n"
                    "Content-Length: 23\r\n"
                    "X-Content-Type-Options: nosniff\r\n\r\n"
                    "404 - Content not found")
                self.request.sendall(not_found_response.encode())
                return
            
            html_content = html_content.replace("{{visits}}", str(MyTCPHandler.visit_count))
        
        elif path == "/chat-messages" and request.method == "POST":
            data = json.loads(request.body)
            message = data.get("message")

            #store chat in database
            chat_collection.insert_one({
                "message": message,
                "username": "Guest",
                #"id": MyTCPHandler.message_id
                })
            #message_id = str(result.inserted_id)  # Get the inserted ID


            response_content = {"message": message}
            #print("rc : " + response_content)
            response_body = json.dumps(response_content)


            response = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: application/json; charset=utf-8\r\n"
            "Content-Length: " + str(len(response_body)) + "\r\n"
            "X-Content-Type-Options: nosniff" + "\r\n\r\n" + response_body
             )
            self.request.sendall(response.encode())

        elif path == "/chat-messages" and request.method == "GET":
            all_data = chat_collection.find({})
            chat_history = list(all_data)
            #print("Chat History (Before Conversion):", chat_history)  # Inspect the _id type


            # Convert ObjectIds to strings
            for item in chat_history:
                if '_id' in item:
                    item['id'] = str(item['_id'])
                    del item['_id']
            #print("Chat History (After Conversion):", chat_history)  # Inspect again
                item['message'] = html.escape(item['message'])


            response_content = chat_history
            #print("Response Content:", response_content)  # Inspect the output 
  
            response_body = json.dumps(response_content)

            response = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: application/json; charset=utf-8\r\n"
                "Content-Length: " + str(len(response_body)) + "\r\n"
                "X-Content-Type-Options: nosniff\r\n\r\n" 
                + response_body
            )
            self.request.sendall(response.encode())


        #if path isnt "/", strip the "/" 
        else:
            path = path.lstrip("/")

        #open requested path and get length of content
        try:    
            with open(path, "rb") as file:
                content = file.read()
                length = len(content)
                #print("length:"+str(length))
        except FileNotFoundError:
                # File not found, respond with a 404 status and a plain text message
                not_found_response = (
                    "HTTP/1.1 404 Not Found\r\n"
                    "Content-Type: text/plain; charset=utf-8\r\n"
                    "Content-Length: 23\r\n"
                    "X-Content-Type-Options: nosniff\r\n\r\n"
                    "404 - Content not found")
                self.request.sendall(not_found_response.encode())
                return
        
       
        #if content type is image or video, dont decode
        if content_type == "image/png" or content_type == "image/jpeg" or content_type == "video/mp4" or content_type == "image/x-icon":

            response = (
            "HTTP/1.1 200 OK OK\r\n"
            "Content-Type: " + content_type + "; charset=utf-8\r\n"
            "Content-Length: " + str(length) + "\r\n"
            "X-Content-Type-Options: nosniff\r\n\r\n")
            
            self.request.sendall(response.encode())
            self.request.sendall(content)

        #if path is for home page, send proper response  with cookies
        elif path == "public/index.html":

            response = (
            "HTTP/1.1 200 OK OK\r\n"
            "Content-Type: " + content_type + "; charset=utf-8\r\n"
            "Content-Length: " + str(len(html_content)) + "\r\n"
            "X-Content-Type-Options: nosniff\r\n" + "Set-Cookie: visits = " + str(MyTCPHandler.visit_count) + "; Max-Age=3600" +"\r\n\r\n" + html_content)
            #response = "HTTP/1.1 200 OK OK\r\nContent-Type: text/plain; charset=utf-8\r\nContent-Length: 13\r\n\r\nHello, World!"
            self.request.sendall(response.encode())
        
     
        else:
            #print("length2:" + str(length))
            response = (
            "HTTP/1.1 200 OK OK\r\n"
            "Content-Type: " + content_type + "; charset=utf-8\r\n"
            "Content-Length: " + str(length) + "\r\n"
            "X-Content-Type-Options: nosniff" + "\r\n\r\n" + content.decode("utf-8"))
            #response = "HTTP/1.1 200 OK OK\r\nContent-Type: text/plain; charset=utf-8\r\nContent-Length: 13\r\n\r\nHello, World!"
            self.request.sendall(response.encode())
        



def main():
    host = "0.0.0.0"
    port = 8080

    socketserver.TCPServer.allow_reuse_address = True

    server = socketserver.TCPServer((host, port), MyTCPHandler)

    print("Listening on port " + str(port))

    server.serve_forever()


if __name__ == "__main__":
    main()
