import secrets
import uuid
import bcrypt
from hashlib import sha256
import html
import json
import socketserver
from bson import ObjectId
from util.request import Request
from util.router import Router
import pymongo
from util.auth import extract_credentials
from util.auth import validate_password
from util.multipart import parse_multipart
import os
from util.websockets import compute_accept
from util.websockets import parse_ws_frame
from util.websockets import generate_ws_frame

clients = {} #dict to store websocketclient objects
authed_clients = []

myclient = pymongo.MongoClient("mongo:27017")
db = myclient["mydatabase"]
chat_collection = db["chat"]
credentials = db["user_pass"]
authed_clientsdb = db["authed_clientsdb"]


class WebSocketClient:
    def __init__(self, handler, username):
       self.handler = handler  # The MyTCPHandler instance associated with the client
       self.username = username

class MyTCPHandler(socketserver.BaseRequestHandler):
    #set visit count var in class
    visit_count = 0
    message_id = 0


    def parse_cookies(self, headers):
        cookies = {}
        #print("cookie headers",headers)
        for header_name, header_value in headers.items():
            if header_name.lower() == "cookie":
                cookie_str = header_value.strip()
                for cookie in cookie_str.split(";"):
                    key, value = cookie.split("=")
                    cookies[key.strip()] = value.strip()
        return cookies

    def handle(self):

        # Parsed_frame = parsed_frame(0,0,0,0,0,0,self)
        # one_byte = self.request.recv(1)
        # frame = Parsed_frame.parse_ws_frame(one_byte)

        received_data = self.request.recv(2048)
        # if len(received_data) == 0:
        #         return
        print(self.client_address)
        print("--- received data ---")
        print(received_data)
        print("--- end of data ---\n\n")
        request = Request(received_data)
         
        content_length = int(request.headers.get('Content-Length',0))

        #store the recieved data in a new variable to use in the while loop
        complete_req = received_data
        index = complete_req.find(b'\r\n\r\n')
        length_from_delimiter = len(complete_req[index + 4:])

        #while loop to buffer data if we have read less than the stated content length
        while length_from_delimiter < content_length:
            next_read = self.request.recv(2048)
            #if the next read is 0, stop the loop
            if not next_read:
                break
            #otherwise, add the next read to the recieved data
            else: 
                complete_req += next_read
                length_from_delimiter = len(complete_req[index + 4:])

        #call request once again with the full request data
        request = Request(complete_req)

        #set path equal to the request path
        path = request.path 
        
        #default content type of empty str
        content_type = ""

              #parse req headers to get cookies
        cookies = self.parse_cookies(request.headers)
        user_authenticated = "auth_token" in cookies

        if "visits" in cookies:
            MyTCPHandler.visit_count = int(cookies["visits"])
            #if visits isnt in cookies, set value to 1
        else:
            MyTCPHandler.visit_count = 0

        #create new router instance var
        router = Router()

        #add routes
        #router.add_route('GET', r'^/websocket/', self.handle_websocket)
        router.add_route('GET', '^/$', self.handle_home)
        router.add_route('GET', '^/chat-messages$', self.handle_chat_messages_get)
        router.add_route('POST', '^/chat-messages$', self.handle_chat_messages_post)
        router.add_route('GET', r'^/public/.*$', self.handle_static)  # Route for static files  
        router.add_route('POST', '^/register$', self.handle_reg) #route for registration 
        router.add_route('POST', '^/login$', self.handle_login) #route for login
        router.add_route('POST', '^/logout$', self.handle_logout) #route for logout
        router.add_route('DELETE', r'^/chat-messages/', self.handle_message_delete)
        router.add_route('POST', '^/upload-media$', self.handle_upload_media)
        router.add_route('GET', '^/public/image/.', self.handle_upload_media)
        router.add_route('GET', '^/public/videos/.', self.handle_upload_media)
        router.add_route('GET', '^/websocket', self.handle_websocket)

        response_bytes = router.route_request(request)
        if response_bytes is not None:
            self.request.sendall(response_bytes)

    
    def handle_websocket(self, request: Request):
        username = "Guest"
        #print("decoded pic header",request.headers.decode('utf-8'))
        cookies = self.parse_cookies(request.headers)
        cookie_auth_token = cookies.get('auth_token')

        if cookie_auth_token:
                token_hash = sha256(cookie_auth_token.encode()).hexdigest()
                user_token = credentials.find_one({"token_hash": token_hash})

                if user_token:
                    username = user_token.get("username")
                    print('username',username)

        random_key = request.headers.get("Sec-WebSocket-Key")
        response_key = compute_accept(random_key)

        switching_protocol_response = (
        b"HTTP/1.1 101 Switching Protocols\r\n" 
        b"Connection: Upgrade\r\n"
        b"Upgrade: websocket\r\n"
        b"Sec-WebSocket-Accept: " + response_key.encode() + b"\r\n\r\n")
        self.request.sendall(switching_protocol_response)

        # Create and store the client 
        client = WebSocketClient(self,username)
        print('client username', client.username)
        clients[self] = client

        #fetch all currently connected clients
        authed_users = authed_clientsdb.find({})
        authed_users = list(authed_users)
        for user in authed_users:
            if user["username"] not in authed_clients:
                authed_clients.append(user["username"])
            self.sendall_websocket('AdduserList','',user["username"],self)

        #self,message_type,message,sender,sender_handle):
        if username != 'Guest' and username not in authed_clients:
             self.sendall_websocket('AdduserList','',username,self)
             authed_clientsdb.insert_one({
                            "username": username,
                            })
        

             

        def buffer_ws_frame(frame, ws_request):
            complete_frame = frame
            bytes_to_read = 0
            while frame.payload_length > len(complete_frame.payload):
                print('buffer started')
                bytes_to_read = min(2048, frame.payload_length - len(complete_frame.payload))
                next_frame = self.request.recv(bytes_to_read)
                #next_frame = self.request.recv(2048)
                ws_request += next_frame
                complete_frame = parse_ws_frame(ws_request)

            return complete_frame
        
        def handle_extra_bytes(self,next_frame):
             if (next_frame.opcode == 1 or next_frame.opcode == 0): #for a text frame
                    print('payload length',next_frame.payload_length)
                    frame_payload = next_frame.payload.decode('utf-8')   #payload {"messageType":"chatMessage","message":"yooooo"}
                    frame_payload = json.loads(frame_payload)
                    #print('payload',frame_payload)
                    message = frame_payload["message"]
                    print('message',message)
                            
                    message_type = frame_payload.get("messageType")
                    sender_handle = self
                    print('sent from next frame if')
                    self.sendall_websocket(message_type,message,username,sender_handle)

    

        #TODO LO3

        def handle_regular_message(self,complete_frame):
            if (complete_frame.opcode == 8): #and not continued_frame:
                print('initiate client disconnect',self)
                try:
                    client_username = clients[self].username
                    del clients[self]
                    authed_clientsdb.delete_one({"username": client_username})

                    if client_username in authed_clients:
                        authed_clients.remove(client_username)

                        self.sendall_websocket('DeluserList','',client_username,self)
                    print('client removed success')
                except KeyError:
                        pass
                return
            elif (complete_frame.opcode == 1 or complete_frame.opcode == 0) and not continued_frame: #for a text frame
                        print('payload length',complete_frame.payload_length)
                        frame_payload = complete_frame.payload.decode('utf-8')   #payload {"messageType":"chatMessage","message":"yooooo"}
                        frame_payload = json.loads(frame_payload)
                        #print('payload',frame_payload)
                        message = frame_payload["message"]
                        print('message',message)
                                
                        message_type = frame_payload.get("messageType")
                        sender_handle = self
                        print('sent from regular message')
                        print('message type',message_type)
                        
                        self.sendall_websocket(message_type,message,username,sender_handle)
            
                
        while True:
            continued_frame = False
            ws_request = self.request.recv(2048)
            if ws_request:
                print('ws request',ws_request)
                frame = parse_ws_frame(ws_request)
                pload = bytearray(frame.payload)
                for byte in range(len(pload)):      #changing to len(payload) to avoid infinite loop
                     pload[byte] = pload[byte] ^ frame.masking_key[byte % 4]
                print('masked payload',bytes(pload))

                #split original ws request by the masked payload, and store the bytes that follow
                byte_string = bytes(pload)

                extra_bytes = ws_request.split(byte_string)[1]
                print('extra bytes', extra_bytes)
         
                stored_payload = bytearray()
                continued_frame = False
                complete_frame = buffer_ws_frame(frame,ws_request)
                if frame.fin_bit == 1:
                    handle_regular_message(self,complete_frame)
                print(complete_frame.payload)

                # # Check if the current frame is continued
                if complete_frame.fin_bit != 1:
                    stored_payload += complete_frame.payload #if its continued, store the payload of that frame
                    continued_frame = True                  #set bool flag to true

                    while complete_frame.fin_bit != 1: 
                        print('fin bit loop')
                        print('before')
                        try:
                            c_ws_request = self.request.recv(2048) #read the next frame
                        except KeyboardInterrupt:
                             pass
                        print('after')
                        c_frame = parse_ws_frame(c_ws_request)  #parse the next frame
                        c_complete_frame = buffer_ws_frame(c_frame,c_ws_request) #buffer the next frame
                        
                        stored_payload += c_complete_frame.payload  #add the payload of the buffered frame to the stored payload byte array
                        if c_complete_frame.fin_bit == 1:           #if the fin bit of the buffered frame == 1, it is the last continued frame
                             print('final continued frame found')
                             break
                         
                while extra_bytes:
                    back2back = True
                    # Process the next frame immediately without waiting for a new request
                    next_frame = parse_ws_frame(extra_bytes)

                    #grab the payload
                    next_pload = next_frame.payload

                    next_pload_2 = bytearray(next_pload)

                    # Unmask the payload of the next frame
                    for byte in range(len(next_pload_2)):
                        next_pload_2[byte] = next_pload_2[byte] ^ next_frame.masking_key[byte % 4]

                    #renmove the frame from the extra bytes string
                    byte_string = bytes(next_pload_2)
                    try: 
                        extra_bytes = ws_request.split(byte_string)[1]
                    except:
                        print('all extra bytes read')
                        handle_extra_bytes(self,next_frame)

                        break
                    print('extra bytes in while',extra_bytes)

                    print('masked payload for next frame', bytes(next_pload_2))
                    print('complete next frame',next_frame.payload)
                    handle_extra_bytes(self,next_frame)

            if continued_frame == True:
                print('length of stored payload',len(stored_payload))
                print('stored payload',stored_payload)

                frame_payload = stored_payload.decode('utf-8')   #payload {"messageType":"","message":"yooooo"}
                print('length of decoded stored payload',len(frame_payload))
                print('stored decoded payload',frame_payload)

                frame_payload = json.loads(frame_payload)
                #print('payload',frame_payload)
                message = frame_payload["message"]
                print('message',message)
                        
                message_type = frame_payload.get("messageType")
                #print('message type',message_type)
                sender_handle = self

                self.sendall_websocket(message_type,message,username,sender_handle)


    def sendall_websocket(self,message_type,message,sender,sender_handle):
                print('beginning of sendall')
                for handle, client_object in clients.items():
                        print('handle',vars(handle))
                    #escape html in message
                        message = html.escape(message)

                        frame = {
                            "messageType": message_type,
                            "username": sender,
                            "message": message,
                            "id": str(uuid.uuid4())
                            }
                        json_string = json.dumps(frame)
                        encoded_frame = json_string.encode()
                        frame_2_send = generate_ws_frame(encoded_frame)
                        print('frame2send',frame_2_send)

                        if message_type == 'AdduserList':
                            if sender not in authed_clients:
                                authed_clients.append(sender)
                            print('authed clients',authed_clients)


                  
                        try:
                            handle.request.sendall(frame_2_send)
                        except:
                            print('tried to send to closed socket')

                if message_type == 'chatMessage':
                    chat_collection.insert_one({
                            "message": message,
                            "username": sender,
                            #"id": MyTCPHandler.message_id
                            })


    #handle registration function
    def handle_reg(self,request: Request):
        username, password = extract_credentials(request)

        if validate_password(password) == False:
             #registration fails 
             return b"HTTP/1.1 302 Found\r\nLocation: /\r\n\r\n"
        else:
             salt = bcrypt.gensalt()
             hashed_password = bcrypt.hashpw(password.encode(), salt)
             credentials.insert_one({
                "username": username,
                "password_hash": hashed_password,
                "salt": salt,
                "token_hash": "",
                "xsrf_token": ""
                })
             return b"HTTP/1.1 302 Found\r\nLocation: /\r\n\r\n"
        
    def handle_login(self,request: Request):
            username, password = extract_credentials(request)

            user_credentials = credentials.find_one({"username": username})

            if user_credentials is not None:
                stored_salt = user_credentials.get("salt")
                stored_password = user_credentials.get("password_hash")

                if bcrypt.checkpw(password.encode(), stored_password):
                    #set cookie to plain text token
                    #store hash of token in db
                    #create token using secrets library
                    token = secrets.token_urlsafe(32)

                    #hash token for db storage
                    hashed_token = sha256(token.encode()).hexdigest()

                    #store the hashed token in db 
                    user_credentials["token_hash"] = hashed_token
                    credentials.update_one({"username": username}, {"$set": user_credentials})

                     # Set the token as a cookie
                    response = (
                    "HTTP/1.1 302 Found\r\n"
                    f"Location: /\r\n"
                    f"Set-Cookie: auth_token={token}; HttpOnly; Max-Age=7200\r\n\r\n"
                    ).encode()

                    self.request.sendall(response)
                    return 


         # If authentication fails, redirect to the home page
            response = b"HTTP/1.1 302 Found\r\nLocation: /\r\n\r\n"
            self.request.sendall(response)
            
    def handle_logout(self, request: Request):
        # Invalidate the user's authentication token 
        cookies = self.parse_cookies(request.headers)
        auth_token = cookies.get('auth_token')

        if auth_token:
            token_hash = sha256(auth_token.encode()).hexdigest()
            user_credentials = credentials.find_one({"token_hash": token_hash})
            user_credentials["token_hash"] = ""
            credentials.update_one({"token_hash": token_hash}, {"$set": {"token_hash": ""}})

        response = (
        "HTTP/1.1 302 Found\r\n"
        "Location: /\r\n"  
        "Set-Cookie: auth_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;\r\n\r\n" 
        ).encode()

        return response 
    
    def handle_message_delete(self, request: Request):
        cookies = self.parse_cookies(request.headers)
        auth_token = cookies.get('auth_token')

        if auth_token:
            token_hash = sha256(auth_token.encode()).hexdigest()
            user_credentials = credentials.find_one({"token_hash": token_hash})

            if user_credentials:
                message_id = request.path.split('/')[-1]

                # Check if the message belongs to the user
                message = chat_collection.find_one({"_id": ObjectId(message_id), "username": user_credentials["username"]})

                if message:
                    # Delete the message
                    chat_collection.delete_one({"_id": ObjectId(message_id), "username": user_credentials["username"]})
                    return b"HTTP/1.1 204 No Content\r\n\r\n"

        response = (
            "HTTP/1.1 403 Forbidden\r\n"
            "\r\n"
        ).encode()

        return response


        #define callback functions
    def handle_home(self, request: Request) -> bytes:
              #if path equals "/" set path to index.html, set content type to text/html, increment cookie count, replace visit count in html file
            path = "public/index.html"
            content_type = "text/html"
            MyTCPHandler.visit_count +=1

            try:
                with open(path, "rb") as html_file:
                    html_content = html_file.read()  # Read as bytes
            except FileNotFoundError:
                # File not found, respond with a 404 status and a plain text message
                 return (
                    "HTTP/1.1 404 Not Found\r\n"
                    "Content-Type: text/plain; charset=utf-8\r\n"
                    "Content-Length: 23\r\n"
                    "X-Content-Type-Options: nosniff\r\n\r\n"
                    "404 - Content not found").encode()
            
            
            cookies = self.parse_cookies(request.headers)
            cookie_auth_token = cookies.get('auth_token')
            user_credentials = None

            if cookie_auth_token:
                token_hash = sha256(cookie_auth_token.encode()).hexdigest()
                user_credentials = credentials.find_one({"token_hash": token_hash})
            
            html_content = html_content.replace(b"{{visits}}", str(MyTCPHandler.visit_count).encode())

            if user_credentials:
                # Replace login form action
                html_content = html_content.replace(b'action="/login"', b'action="/logout"')

                # Replace the label of the button
                html_content = html_content.replace(b'<input type="submit" value="Post" id="login-post-button">', b'<input type="submit" value="Logout" id="login-post-button">')

                # Retrieve existing token if found, otherwise generate a new one
                xsrf_token = user_credentials.get('xsrf_token')
                if xsrf_token == "":
                     xsrf_token = secrets.token_urlsafe(32) 

                # Update user credentials to make sure the token is stored
                user_credentials['xsrf_token'] = xsrf_token
                credentials.update_one({"token_hash": token_hash}, {"$set": {"xsrf_token": xsrf_token}})
                #print(user_credentials)
                html_content = html_content.replace(b'{{xsrf_token}}', xsrf_token.encode()) 



            # send proper response  with cookies
            response = (
            "HTTP/1.1 200 OK OK\r\n"
            "Content-Type: " + content_type + "; charset=utf-8\r\n"
            "Content-Length: " + str(len(html_content)) + "\r\n"
            "X-Content-Type-Options: nosniff\r\n" + "Set-Cookie: visits = " + str(MyTCPHandler.visit_count) + "; Max-Age=3600" +"\r\n\r\n").encode() + html_content

            return response

    def handle_chat_messages_get(self, request: Request) -> bytes:
            all_data = chat_collection.find({})
            chat_history = list(all_data)
            # Convert ObjectIds to strings
            for item in chat_history:
                if '_id' in item:
                    item['id'] = str(item['_id'])
                    del item['_id']
                #if its a message, dont escape
                if item['message'].startswith("<img src=") or item['message'].startswith("<video width="):
                     continue
                else:
                    item['message'] = html.escape(item['message'])


            response_content = chat_history  
            response_body = json.dumps(response_content)

            response = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: application/json; charset=utf-8\r\n"
                "Content-Length: " + str(len(response_body)) + "\r\n"
                "X-Content-Type-Options: nosniff\r\n\r\n" 
                + response_body
            )
            self.request.sendall(response.encode()) 

    def handle_chat_messages_post(self, request: Request) -> bytes:
            username = "Guest"
            data = json.loads(request.body)
            message = data.get("message")

            cookies = self.parse_cookies(request.headers)
            cookie_auth_token = cookies.get('auth_token')

            if cookie_auth_token:
                token_hash = sha256(cookie_auth_token.encode()).hexdigest()
                user_token = credentials.find_one({"token_hash": token_hash})

                if user_token:
                    username = user_token.get("username")

                    submitted_xsrf_token = request.headers.get('X-XSRF-Token')
                    expected_xsrf_token = user_token.get('xsrf_token')

                    if submitted_xsrf_token != expected_xsrf_token:
                        return b"HTTP/1.1 403 Forbidden\r\n\r\n"  # XSRF token mismatch

            #store chat in database
            chat_collection.insert_one({
                "message": message,
                "username": username,
                #"id": MyTCPHandler.message_id
                })
            #message_id = str(result.inserted_id)  # Get the inserted ID


            response_content = {"message": message}
            response_body = json.dumps(response_content)


            response = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: application/json; charset=utf-8\r\n"
            "Content-Length: " + str(len(response_body)) + "\r\n"
            "X-Content-Type-Options: nosniff" + "\r\n\r\n" + response_body
             )
            self.request.sendall(response.encode()) 

    def handle_upload_media(self, request: Request) -> bytes:
        
        username = "Guest"
        cookies = self.parse_cookies(request.headers)
        cookie_auth_token = cookies.get('auth_token')


        if cookie_auth_token:
                token_hash = sha256(cookie_auth_token.encode()).hexdigest()
                user_token = credentials.find_one({"token_hash": token_hash})

                if user_token:
                    username = user_token.get("username")

        multi_response = parse_multipart(request)

        for piece in multi_response.parts:
            if piece.headers["Content-Type"] == "image/jpeg":
                # Generate filename and create the full path
                existing_images = len(list(os.listdir("public/image")))
                file_name = f"image_{existing_images + 1}.jpg"  # Generate a new filename
                full_path = os.path.join("public/image/", file_name)


                with open(full_path, "wb") as f:
                    for part in multi_response.parts:
                        if part.name == "media":
                            #("content",part.content)
                            f.write(part.content)

                # Update the database (adjust as needed)
                chat_collection.insert_one({
                    "message": f"<img src='/public/image/{file_name}' class='uploaded-image'>", 
                    "username": username
                })
            elif piece.headers["Content-Type"] == "video/mp4":
                videos_path = "public"
                videos_directory = os.path.join(videos_path, "videos")
                
                if not os.path.exists(videos_directory):
                    # Create  "videos" directory if it doesn't exist
                    os.makedirs(videos_directory)

                existing_videos = len(list(os.listdir("public/videos")))
                file_name = f"video_{existing_videos + 1}.mp4"  # Generate a new filename
                full_path = os.path.join("public/videos/", file_name)

                with open(full_path, "wb") as f:
                    for part in multi_response.parts:
                        if part.name == "media":
                            f.write(part.content)

                chat_collection.insert_one({
                    "message":  f'<video width="400" controls autoplay muted><source src="{full_path}" type="video/mp4"></video>',  
                    "username": username
                })


        response = b"HTTP/1.1 302 Found\r\nLocation: /\r\n\r\n"
        self.request.sendall(response)


    def handle_static(self, request: Request) -> bytes:
        #content_length = int(request.headers.get('Content-Length'))
             #if path isnt "/", strip the "/" 
        path = request.path.lstrip("/")  # Get the path from the request

        #open requested path and get length of content
        try:    
            with open(path, "rb") as file:
                content = file.read()
                length = len(content)
        except FileNotFoundError:
                # File not found, respond with a 404 status and a plain text message
                 return (
                    "HTTP/1.1 404 Not Found\r\n"
                    "Content-Type: text/plain; charset=utf-8\r\n"
                    "Content-Length: 23\r\n"
                    "X-Content-Type-Options: nosniff\r\n\r\n"
                    "404 - Content not found".encode())
                
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
    
        response = (
        b"HTTP/1.1 200 OK\r\n" 
        b"Content-Type: " + content_type.encode() + b"; charset=utf-8\r\n"
        b"Content-Length: " + str(length).encode('utf-8') + b"\r\n"
        b"X-Content-Type-Options: nosniff\r\n\r\n" + content) 

        return response


def main():
    host = "0.0.0.0"
    port = 8080

    socketserver.ThreadingTCPServer.allow_reuse_address = True

    server = socketserver.ThreadingTCPServer((host, port), MyTCPHandler)

    print("Listening on port " + str(port))

    server.serve_forever()


if __name__ == "__main__":
    main()
