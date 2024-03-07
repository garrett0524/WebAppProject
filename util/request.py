class Request:

    def __init__(self, request: bytes):
        # TODO: parse the bytes of the request and populate the following instance variables

        #split request for body (should be in bytes)
        body = request.split(b"\r\n\r\n",1)

        #decode the request, now a str
        request_str = request.decode('utf-8')

        #split the decoded str into part before the header
        line_before_header = request_str.split('\r\n')[0]

        #set variables to their respective part of the decoded str
        self.body = body[1]
        self.method = line_before_header.split()[0]
        self.path = line_before_header.split()[1] 
        self.http_version = line_before_header.split()[2] 
        self.headers = {}
        self.cookies = {}



        #extract and populate headers variable
        #split request str by newline
        lines = request_str.split('\r\n')
        #skip first part
        headers = lines[1:]
        #loop to iterate headers
        for header in headers:
                if not header:
                     break
                #set name and value by splitting by colon space
                #print("header: " + header)
                name, value = header.split(": ", 1)
                #populate headers dictionary
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
     


            
             
        




def test1():
    request = Request(b'GET / HTTP/1.1\r\nHost: localhost:8080\r\nConnection: keep-alive\r\n\r\n')
    assert request.method == "GET"
    assert "Host" in request.headers
    assert request.headers["Host"] == "localhost:8080"  # note: The leading space in the header value must be removed
    #assert request.body == b""  # There is no body for this request.
    # When parsing POST requests, the body must be in bytes, not str

    # This is the start of a simple way (ie. no external libraries) to test your code.
    # It's recommended that you complete this test and add others, including at least one
    # test using a POST request. Also, ensure that the types of all values are correct

def test_get_with_body():
    request = Request(b'GET / HTTP/1.1\r\nHost: localhost:8080\r\nConnection: keep-alive\r\n\r\nThis is the body content')
    assert request.method == "GET"
    assert "Host" in request.headers
    assert request.headers["Host"] == "localhost:8080"  # Ensure the correct Host value is parsed
    assert request.body == b'This is the body content'  # Check that the body is correctly parsed


def test_get_request_with_cookies():
    request_data = b'GET / HTTP/1.1\r\nHost: localhost:8080\r\nConnection: keep-alive\r\nCookie: username=johndoe; sessionid=123456\r\n\r\n'
    request = Request(request_data)
    
    assert request.method == "GET"
    assert "Host" in request.headers
    assert request.headers["Host"] == "localhost:8080"
    assert "Cookie" in request.headers
    assert request.headers["Cookie"] == "username=johndoe; sessionid=123456"

    assert "username" in request.cookies
    assert request.cookies["username"] == "johndoe"
    assert "sessionid" in request.cookies
    assert request.cookies["sessionid"] == "123456"

def test_post_request_with_cookies():
    request_data = b'POST / HTTP/1.1\r\nHost: localhost:8080\r\nConnection: keep-alive\r\nCookie: username=doejohn; sessionid=654321\r\n\r\nThis is the request body content'
    request = Request(request_data)
    
    assert request.method == "POST"
    assert "Host" in request.headers
    assert request.headers["Host"] == "localhost:8080"
    assert "Cookie" in request.headers
    assert request.headers["Cookie"] == "username=doejohn; sessionid=654321"

    assert "username" in request.cookies
    assert request.cookies["username"] == "doejohn"
    assert "sessionid" in request.cookies
    assert request.cookies["sessionid"] == "654321"

    assert request.body == b'This is the request body content'



if __name__ == '__main__':
    test1()
    test_get_with_body()
    test_get_request_with_cookies()
    test_post_request_with_cookies()
    