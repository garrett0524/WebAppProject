import re
from util.request import Request

class Part:
    def __init__(self, headers, name, content):
        self.headers = headers
        self.name = name
        self.content = content

class Boundary_parts:
     def __init__(self,boundary,parts):
        self.boundary = boundary
        self.parts = parts

    

def parse_multipart(request: Request):
        print('full multipart request',len(request.body))
        #print('body content',request.body)
        #parse the boundary from the start of the request
        content_type = request.headers["Content-Type"]
        boundary = re.search(r"boundary=(.+)", content_type).group(1)  
        full_boundary = b"--" + boundary.encode()

        #list to store parts of request
        parts = []
        #use loop to split parts of multipart request by boundary and store as object          
        for piece in request.body.split(full_boundary):
            if b'\r\n\r\n' in piece:
                #split the piece into its headers and its content and assign variables
                header_lines, content = piece.split(b'\r\n\r\n', 1)
                #print('just the content',content)
                print('length of content',len(content))

                #dict to store headers key value pair
                headers= {}
                #print(headers)
                #iterate the header_lines variable to populate the Part object
                for line in header_lines.decode().splitlines():
                    if ': ' in line:
                        key, value = line.split(': ', 1)
                        headers[key] = value
                #print(headers)

                #get content from headers dict
                content_disposition = headers.get("Content-Disposition")
                #initialize name
                name = ""
                if content_disposition!= None:
                    #set content_parts = to the split of content_dispo
                    content_parts = content_disposition.split('; ')[1]
                    #get the name from content_parts variable and set equal to new variable
                    if 'name=' in content_parts:
                        name = content_parts.split('name=')[1].strip('"')

                #popuate object
                part = Part(headers,name,content.strip())
                #append object to list
                parts.append(part)
        return_obj =Boundary_parts(boundary,parts)
        return return_obj  # Return the list of parts

def test_multipart():

    raw_request_data = b'POST /upload-pic HTTP/1.1\r\nHost: localhost:8080\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\nSec-Fetch-Site: same-origin\r\nAccept-Language: en-US,en;q=0.9\r\nAccept-Encoding: gzip, deflate\r\nSec-Fetch-Mode: navigate\r\nContent-Type: multipart/form-data; boundary=----WebKitFormBoundaryHWsspClnN7YZEd4C\r\nOrigin: http://localhost:8080\r\nUser-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3.1 Safari/605.1.15\r\nReferer: http://localhost:8080/\r\nUpgrade-Insecure-Requests: 1\r\nContent-Length: 1033613\r\nConnection: keep-alive\r\nSec-Fetch-Dest: document\r\nCookie: visits=101; auth_token=iMGDE62RoKfellLyazMlfoLfqiK17fLYvmB39X2Fa8I\r\n\r\n------WebKitFormBoundaryHWsspClnN7YZEd4C\r\nContent-Disposition: form-data; name="image"; filename="Sample-jpg-image-1mb.jpg"\r\nContent-Type: image/jpeg\r\n\r\n\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xe1\x12\x14Exif\x00\x00MM\x00*\x00\x00\x00\x08\x00\x0b\x01\x0f\x00\x02\x00\x00\x00\x06\x00\x00\x00\x92\x01\x10\x00\x02\x00\x00\x00\n\x00\x00\x00\x98\x01\x12\x00\x03\x00\x00\x00\x01\x00\x01\x00\x00\x01\x1a\x00\x05\x00\x00\x00\x01\x00\x00\x00\xa2\x01\x1b\x00\x05\x00\x00\x00\x01\x00\x00\x00\xaa\x01(\x00\x03\x00\x00\x00\x01\x00\x02\x00\x00\x011\x00\x02\x00\x00\x00\x07\x00\x00\x00\xb2\x012\x00\x02\x00\x00\x00\x14\x00\x00\x00\xba\x02\x13\x00\x03\x00\x00\x00\x01\x00\x01\x00\x00\x87i\x00\x04\x00\x00\x00\x01\x00\x00\x00\xce\x88%\x00\x04\x00\x00\x00\x01\x00\x00\x06N\x00\x00\x07\x86Apple\x00iPhone 6s\x00\x00\x00\x00H\x00\x00\x00\x01\x00\x00\x00H\x00\x00\x00\x0110.1.1\x00\x002016:12:02 11:10:20\x00\x00!\x82\x9a\x00\x05\x00\x00\x00\x01\x00\x00\x02`\x82\x9d\x00\x05\x00\x00\x00\x01\x00\x00\x02h\x88"\x00\x03\x00\x00\x00\x01\x00\x02\x00\x00\x88\'\x00\x03\x00\x00\x00\x01\x00\x19\x00\x00\x90\x00\x00\x07\x00\x00\x00\x040221\x90\x03\x00\x02\x00\x00\x00\x14\x00\x00\x02p\x90\x04\x00\x02\x00\x00\x00\x14\x00\x00\x02\x84\x91\x01\x00\x07\x00\x00\x00\x04\x01\x02\x03\x00\x92\x01\x00\n\x00\x00\x00\x01\x00\x00\x02\x98\x92\x02\x00\x05\x00\x00\x00\x01\x00\x00\x02\xa0\x92\x03\x00\n\x00\x00\x00\x01\x00\x00\x02\xa8\x92\x04\x00\n\x00\x00\x00\x01\x00\x00\x02\xb0\x92\x07\x00\x03\x00\x00\x00\x01\x00\x05\x00\x00\x92\t\x00\x03\x00\x00\x00\x01\x00\x18\x00\x00\x92\n\x00\x05\x00\x00\x00\x01\x00\x00\x02\xb8\x92\x14\x00\x03\x00\x00\x00\x04\x00\x00\x02\xc0\x92|\x00\x07\x00\x00\x03:\x00\x00\x02\xc8\x92\x91\x00\x02\x00\x00\x00\x04955\x00\x92\x92\x00\x02\x00\x00\x00\x04955\x00\xa0\x00\x00\x07\x00\x00\x00\x040100\xa0\x01\x00\x03\x00\x00\x00\x01\x00\x01\x00\x00\xa0\x02\x00\x04\x00\x00\x00\x01\x00\x00\x0f\xc0\xa0\x03\x00\x04\x00\x00\x00\x01\x00\x00\x0b\xd0\xa2\x17\x00\x03\x00\x00\x00\x01\x00\x02\x00\x00\xa3\x01\x00\x07\x00\x00\x00\x01\x01\x00\x00\x00\xa4\x02\x00\x03\x00\x00\x00\x01\x00\x00\x00\x00\xa4\x03\x00\x03\x00\x00\x00\x01\x00\x00\x00\x00\xa4\x05\x00\x03\x00\x00\x00\x01\x00\x1d\x00\x00\xa4\x06\x00\x03\x00\x00\x00\x01\x00\x00\x00\x00\xa42\x00\x05\x00\x00\x00\x04\x00\x00\x06\x02\xa43\x00\x02\x00\x00\x00\x06\x00\x00\x06"\xa44\x00\x02\x00\x00\x00#\x00\x00\x06(\xea\x1d\x00\t\x00\x00\x00\x01\x00\x00\x00\x0c\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x10\xb2\x00\x00\x00\x0b\x00\x00\x00\x052016:12:02 11:10:20\x002016:12:02 11:10:20\x00\x00\x00-k\x00\x00\x03\xc4\x00\x00\x1f/\x00\x00\r\xb5\x00\x00G\xea\x00\x00\x05\xe3\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00S\x00\x00\x00\x14\x07\xdf\x05\xe7\x08\xa9\x052Apple iOS\x00\x00\x01MM\x00\n\x00\x01\x00\t\x00\x00\x00\x01\x00\x00\x00\x04\x00\x02\x00\x07\x00\x00\x02.\x00\x00\x00\x8c\x00\x03\x00\x07\x00\x00\x00h\x00\x00\x02\xba\x00\x04\x00\t\x00\x00\x00\x01\x00\x00\x00\x01\x00\x05\x00\t\x00\x00\x00\x01\x00\x00\x00\xed\x00\x06\x00\t\x00\x00\x00\x01\x00\x00\x00\xe8\x00\x07\x00\t\x00\x00\x00\x01\x00\x00\x00\x01\x00\x08\x00\n\x00\x00\x00\x03\x00\x00\x03"\x00\x0e\x00\t\x00\x00\x00\x01\x00\x00\x00\x00\x00\x14\x00\t\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00bplist00O\x11\x02\x00\xa6\x00\x9a\x00\x94\x00\x99\x00\xa2\x00\xbc\x00\xf7\x00P\x01\x8a\x02:\x03\xf8\x01"\x01\x00\x01\xce\x00L\x00,\x00\x9d\x00\x94\x00\x90\x00\x95\x00\xa3\x00\xc5\x00\t\x01h\x01B\x02\xa7\x01%\x01\xf9\x00\xda\x00\xbe\x00\xa2\x00)\x00\x91\x00\x8b\x00\x8c\x00\x93\x00\xa4\x00\xcd\x00\x1d\x01\x80\x01\x89\x01\x06\x01\xe5\x00\xd1\x00\xc4\x00\xbd\x00\xfd\x00r\x00\x88\x00\x85\x00\x87\x00\x91\x00\xa7\x00\xd7\x001\x01j\x01,\x01\xce\x00\xc0\x00\xb8\x00\x89\x00\xa9\x00\x04\x01\xe5\x00\x80\x00\x83\x00\x85\x00\x93\x00\xab\x00\xe3\x00B\x01"\x01\xe1\x00\xaf\x00\xaf\x00\xb5\x00t\x00\xad\x00\x08\x01\x16\x01x\x00|\x00\x81\x00\x91\x00\xb0\x00\xf1\x008\x01\xe0\x00\xa9\x00\xa1\x00\x95\x00\xf0\x00y\x00\xb9\x00\x0f\x01\x1f\x01t\x00v\x00\x80\x00\x92\x00\xb7\x00\x03\x01\x15\x01\xba\x00\xa3\x00\xee\x00\x97\x00\x0e\x01\x7f\x00\xcf\x00\x1b\x01&\x01r\x00t\x00\x7f\x00\x93\x00\xbf\x00\x16\x01\xde\x00\xa9\x00\xf2\x00[\x01\xba\x006\x01\x85\x00\xf4\x00(\x01\'\x01n\x00s\x00\x7f\x00\x98\x00\xc9\x00\x11\x01\xbb\x00\x9f\x00L\x01u\x01\xed\x00K\x01\x88\x00\x1c\x01+\x01)\x01n\x00t\x00\x80\x00\x9d'
    #raw_request_data = b'POST /form-path HTTP/1.1\r\nContent-Length: 252\r\nContent-Type: multipart/form-data; boundary=----WebKitFormBoundaryfkz9sCA6fR3CAHN4\r\n\r\n------WebKitFormBoundaryfkz9sCA6fR3CAHN4\r\nContent-Disposition: form-data; name="commenter"\r\n\r\nJesse\r\n------WebKitFormBoundaryfkz9sCA6fR3CAHN4\r\nContent-Disposition: form-data; name="comment"\r\n\r\nGood morning!\r\n------WebKitFormBoundaryfkz9sCA6fR3CAHN4--'
    mock_request = Request(raw_request_data)
    #print("mock method",mock_request.method)
    #print("mock path",mock_request.path)
    

    # Call  and store result
    result = parse_multipart(mock_request)
    print(result.boundary)
    #x = False
    #for part in result:
        #print("Name:", part.name)
        #print("Headers:", part.headers)
        #print(part.headers["Content-Type"])
        # print("Content:", part.content)  
        #  if part.name == "image":
        #             print("content",part.content)




#if __name__ == '__main__':
    #test_parse_multipart()


#     #assert individual parts
    
#     # assert result[0].name == "commenter"  
#     # assert result[0].content == b"Jesse"

#     # assert result[1].name == "comment" 
#     # assert result[1].content == b"Good morning!"

if __name__ == '__main__':
      test_multipart()
      #test_parse_multipart()
