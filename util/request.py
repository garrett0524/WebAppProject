class Request:

    def __init__(self, request: bytes):
        #print(f"Raw request data (length: {len(request)}): {request}")
        # TODO: parse the bytes of the request and populate the following instance variables

        #split request for body (should be in bytes)
        body = request.split(b"\r\n\r\n",1)

        multipart_request = False
        #decode the request, now a str
        if b"multipart" not in request:
            multipart_request = False
            request_str = request.decode('utf-8')
        else:
            multipart_request = True
            request_str = request

        #split the decoded str into part before the header

        if multipart_request == False:
            line_before_header = request_str.split('\r\n')[0]
        else:
            line_before_header = request_str.split(b'\r\n')[0]

        #set variables to their respective part of the decoded str
        self.body = body[1]
        if multipart_request == False:
            self.method = line_before_header.split()[0]
            self.path = line_before_header.split()[1] 

        else:
            self.method = line_before_header.split()[0].decode('utf-8')
            self.path = line_before_header.split()[1].decode('utf-8')

        self.http_version = line_before_header.split()[2] 
        self.headers = {}
        self.cookies = {}



        #extract and populate headers variable
        #split request str by newline

        if multipart_request == False:
            lines = request_str.split('\r\n')
        else:
            lines = request_str.split(b'\r\n')
        #skip first part
        headers = lines[1:]
        #loop to iterate headers
        for header in headers:
                if not header:
                     break
                #set name and value by splitting by colon space
                #print("header: " + header)
                if multipart_request == False:
                    name, value = header.split(": ", 1)
                else:
                    name, value = header.split(b": ", 1)
                #populate headers dictionary
                if multipart_request:
                    self.headers[name.decode('utf-8')] = value.decode('utf-8')
                else:
                    self.headers[name] = value


        #extract and populate cookies variable
        #if "cookie" is found in headers
        if "Cookie" in self.headers:
                #set cookies_str to the string of cookies
                cookies_str = self.headers["Cookie"]
                #break string down into each cookie
                cookie_pairs = cookies_str.split(';')
                #loop to iterate cookie pairs
                for cookie_pair in cookie_pairs:
                    if not cookie_pair:
                        break
                    #split cookie pair into key and value using = as delimiter
                    key, value = cookie_pair.split('=', 1)
                    #populate cookies dictionary with stripped key and value
                    self.cookies[key.strip()] = value.strip()
     


            
             
        




# def test1():
#     request = Request(b'GET / HTTP/1.1\r\nHost: localhost:8080\r\nConnection: keep-alive\r\n\r\n')
#     assert request.method == "GET"
#     assert "Host" in request.headers
#     assert request.headers["Host"] == "localhost:8080"  # note: The leading space in the header value must be removed
#     #assert request.body == b""  # There is no body for this request.
#     # When parsing POST requests, the body must be in bytes, not str

#     # This is the start of a simple way (ie. no external libraries) to test your code.
#     # It's recommended that you complete this test and add others, including at least one
#     # test using a POST request. Also, ensure that the types of all values are correct

# def test_get_with_body():
#     request = Request(b'GET / HTTP/1.1\r\nHost: localhost:8080\r\nConnection: keep-alive\r\n\r\nThis is the body content')
#     assert request.method == "GET"
#     assert "Host" in request.headers
#     assert request.headers["Host"] == "localhost:8080"  # Ensure the correct Host value is parsed
#     assert request.body == b'This is the body content'  # Check that the body is correctly parsed


# def test_get_request_with_cookies():
#     request_data = b'GET / HTTP/1.1\r\nHost: localhost:8080\r\nConnection: keep-alive\r\nCookie: username=johndoe; sessionid=123456\r\n\r\n'
#     request = Request(request_data)
    
#     assert request.method == "GET"
#     assert "Host" in request.headers
#     assert request.headers["Host"] == "localhost:8080"
#     assert "Cookie" in request.headers
#     assert request.headers["Cookie"] == "username=johndoe; sessionid=123456"

#     assert "username" in request.cookies
#     assert request.cookies["username"] == "johndoe"
#     assert "sessionid" in request.cookies
#     assert request.cookies["sessionid"] == "123456"

# def test_post_request_with_cookies():
#     request_data = b'POST / HTTP/1.1\r\nHost: localhost:8080\r\nConnection: keep-alive\r\nCookie: username=doejohn; sessionid=654321\r\n\r\nThis is the request body content'
#     request = Request(request_data)
    
#     assert request.method == "POST"
#     assert "Host" in request.headers
#     assert request.headers["Host"] == "localhost:8080"
#     assert "Cookie" in request.headers
#     assert request.headers["Cookie"] == "username=doejohn; sessionid=654321"

#     assert "username" in request.cookies
#     assert request.cookies["username"] == "doejohn"
#     assert "sessionid" in request.cookies
#     assert request.cookies["sessionid"] == "654321"

#     assert request.body == b'This is the request body content'

# def test123():
#     request_data =b'POST /profile-pic HTTP/1.1\r\nHost: localhost:8080\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\nSec-Fetch-Site: same-origin\r\nAccept-Language: en-US,en;q=0.9\r\nAccept-Encoding: gzip, deflate\r\nSec-Fetch-Mode: navigate\r\nContent-Type: multipart/form-data; boundary=----WebKitFormBoundarywfBl08hY9HAIUWWM\r\nOrigin: http://localhost:8080\r\nUser-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3.1 Safari/605.1.15\r\nReferer: http://localhost:8080/\r\nUpgrade-Insecure-Requests: 1\r\nContent-Length: 205779\r\nConnection: keep-alive\r\nSec-Fetch-Dest: document\r\nCookie: visits=3\r\n\r\n'
#     request = Request(request_data)
#     print(request.headers)
#     #print(request.cookies.get(b'visits').decode('utf-8'))
#     #print(boundary)

def test_contentlength():
    request_data = b'POST /upload-media HTTP/1.1\r\nHost: localhost:8080\r\nConnection: keep-alive\r\nContent-Length: 15317714\r\nCache-Control: max-age=0\r\nsec-ch-ua: "Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"\r\nsec-ch-ua-mobile: ?0\r\nsec-ch-ua-platform: "macOS"\r\nUpgrade-Insecure-Requests: 1\r\nOrigin: http://localhost:8080\r\nContent-Type: multipart/form-data; boundary=----WebKitFormBoundarynyTbAiLQTv8n2Kue\r\nUser-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7\r\nSec-Fetch-Site: same-origin\r\nSec-Fetch-Mode: navigate\r\nSec-Fetch-User: ?1\r\nSec-Fetch-Dest: document\r\nReferer: http://localhost:8080/\r\nAccept-Encoding: gzip, deflate, br, zstd\r\nAccept-Language: en-US,en;q=0.9\r\nCookie: visits=1\r\n\r\n------WebKitFormBoundarynyTbAiLQTv8n2Kue\r\nContent-Disposition: form-data; name="media"; filename="sample-3.mp4"\r\nContent-Type: video/mp4\r\n\r\n\x00\x00\x00 ftypisom\x00\x00\x02\x00isomiso2avc1mp41\x00\x00\x00\x08free\x00\xe9\x92\xb0mdat\x00\x00\x02\xae\x06\x05\xff\xff\xaa\xdcE\xe9\xbd\xe6\xd9H\xb7\x96,\xd8 \xd9#\xee\xefx264 - core 155 r2917 0a84d98 - H.264/MPEG-4 AVC codec - Copyleft 2003-2018 - http://www.videolan.org/x264.html - options: cabac=1 ref=3 deblock=1:0:0 analyse=0x3:0x113 me=hex subme=7 psy=1 psy_rd=1.00:0.00 mixed_ref=1 me_range=16 chroma_me=1 trellis=1 8x8dct=1 cqm=0 deadzone=21,11 fast_pskip=1 chroma_qp_offset=-2 threads=6 lookahead_threads=1 sliced_threads=0 nr=0 decimate=1 interlaced=0 bluray_compat=0 constrained_intra=0 bframes=3 b_pyramid=2 b_adapt=1 b_bias=0 direct=1 weightb=1 open_gop=0 weightp=2 keyint=250 keyint_min=25 scenecut=40 intra_refresh=0 rc_lookahead=40 rc=crf mbtree=1 crf=21.0 qcomp=0.60 qpmin=0 qpmax=69 qpstep=4 ip_ratio=1.40 aq=1:1.00\x00\x80\x00\x01\x96\x89e\x88\x84\x00O\xfb\xe4\x1f\x02\x99\xdf\xeaw^_SC@m?\xec\xa1\xba\xe9\xdc\xda\xb8\xd0D\x11\xb3\x18IR\xef*/\xcb\xb5J\xb9\x82\x99\xe6\xd2M6\x8b\xfb\xcb\x9d\xdf\x1b\xb8\x1ax\x06ls}\x9b\x84\x89\xeb\xbc\xffg\xd7_\x0b\xe17\x1c\xa1\r\xfa\xb2\xbe\x9f3\xe2\xd3p\xa6\x00\x1e-\x9a\xa3*W\xc6s\x8ac\x89\xcd\x19\xfes!$\x1b\xf2\xf4\x1cu\x9f}R\xd3}\x9em\xeegF\xb1en\xc4\x0f\x89~a"\xd9\x90\xc7u\x12\x93\n\xc8\\\xff*\x9b~\x8e9z\xd1\xbb\xbe\x85\xe8\xd3\x8a\xe0\xcex\xb3\xa6\x80\xe0\x13\x82\x82r\xf4P\xcd\x9f?*L\x84\xfb"o*\xb6\xad\\X\x0b\x9f\xfcC\x95\xd5m\xd0\xd3jMy?X\xbb\n\xc9\xd6\xd3N\xfe\xd4Y\x8c\xf2\\|\xb8\x1d\xb7S\x8cx\xb7\xee\xe1\'\xe6\xde\xc7\xec\x0b(\x85\xf0\xdd\xd7\xe8\rOD\xfe\x12\x13\x13\xa9\x98\xaf\xf4m|:\xc0;j\x82\x18\xea_\xba\xc3f\xf9^\x98\xc2x\xc8\x0b((5\x92\xd3'
    request = Request(request_data)
    print(request.body)

if __name__ == '__main__':
    test_contentlength()
#     test1()
#     test_get_with_body()
#     test_get_request_with_cookies()
#     test_post_request_with_cookies()
     #test123()
    