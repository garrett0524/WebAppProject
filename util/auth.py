from util.request import Request

def extract_credentials(request: Request):
    #set to empty string to initialize
    username = ""
    password = ""

    #decode body
    decoded_body = request.body.decode('utf-8')


    #split on & to get key and value
    split_string = decoded_body.split('&')
    #print(split_string)

    #loop through user_passs to find user and pass
    for user_pass in split_string:
        if "=" in user_pass:
            key, value = user_pass.split('=')
            if key == "username_login" or key == "username_reg":
                username = value.replace('%21', '!').replace('%40', '@').replace('%23', '#').replace('%24', '$') \
                    .replace('%5E', '^').replace('%26', '&').replace('%28', '(') \
                    .replace('%29', ')').replace('%2D', '-').replace('%5F', '_').replace('%3D', '=').replace('%25', '%')
            elif key == 'password_login' or key == "password_reg":
                password = value.replace('%21', '!').replace('%40', '@').replace('%23', '#').replace('%24', '$') \
                    .replace('%5E', '^').replace('%26', '&').replace('%28', '(') \
                    .replace('%29', ')').replace('%2D', '-').replace('%5F', '_').replace('%3D', '=').replace('%25', '%')

    return [username, password]

def validate_password(string):
    meets_criteria = True

    if len(string) < 8:
        meets_criteria = False
    
    special_chars = {'!', '@', '#', '$', '%', '^', '&', '(', ')', '-', '_', '='}

    lowercase_exists = False
    uppercase_exists = False
    has_num = False
    has_special_char = False
    has_invalid_char = False



    for letter in string:
        if letter.islower():
            lowercase_exists = True
        elif letter.isupper():
            uppercase_exists = True
        elif letter.isdigit():
            has_num = True
        elif letter in special_chars:
            has_special_char = True

        else:
            has_invalid_char = True
    


    if lowercase_exists == False:
        meets_criteria = False

    if uppercase_exists == False:
        meets_criteria = False

    if has_num == False:
        meets_criteria = False

    if has_special_char == False:
        meets_criteria = False
    
    if has_invalid_char == True:
        meets_criteria = False
    
    return meets_criteria


# def test_empty():
#     request_str = b'POST / HTTP/1.1\r\nHost: localhost:8080\r\nConnection: keep-alive\r\n\r\n'
#     request = Request(request_str)
#     result = extract_credentials(request)
#     assert result == ["", ""]

# def test_regular():
#     request_str = b'POST / HTTP/1.1\r\nHost: localhost:8080\r\nConnection: keep-alive\r\n\r\n' \
#                   b'username=testuser&password=testpassword'
#     request = Request(request_str)
#     result = extract_credentials(request)
#     assert result == ["testuser", "testpassword"]

# def test_with_special_chars():
#     request_str = b'POST / HTTP/1.1\r\nHost: localhost:8080\r\nConnection: keep-alive\r\n\r\n' \
#                   b'username_login=testuser&password_login=test%21pass%40word%23%24%25%5E%26%28%29%2D%5F%3D'
#     request = Request(request_str)
#     result = extract_credentials(request)
#     assert result == ["testuser", "test!pass@word#$%^&()-_="]

# def test_malformed_form_data():
#     request_str = b'POST / HTTP/1.1\r\nHost: localhost:8080\r\nConnection: keep-alive\r\n\r\njustastringwithoutkeyvaluepairs'
#     request = Request(request_str)
#     result = extract_credentials(request)
#     assert result == ["", ""]

# def test_registration():
#     request_str = b'POST /register HTTP/1.1\r\nHost: localhost:8080\r\nConnection: keep-alive\r\n\r\n' \
#                   b'username=newuser&password=secretpassword'
#     request = Request(request_str)
#     result = extract_credentials(request)
#     assert result == ["newuser", "secretpassword"]

# def test_login():
#     request_str = b'POST /login HTTP/1.1\r\nHost: localhost:8080\r\nConnection: keep-alive\r\n\r\n' \
#                   b'username=existinguser&password=existingpassword'
#     request = Request(request_str)
#     result = extract_credentials(request)
#     assert result == ["existinguser", "existingpassword"]

# def test_login_request():
#     request_str = b'POST /login HTTP/1.1\r\nHost: localhost:8080\r\nConnection: keep-alive\r\n\r\n' \
#                   b'username_login=existinguser&password_login=existingpassword'
#     request = Request(request_str)
#     result = extract_credentials(request)
#     #print(result)
#     assert result == ["existinguser", "existingpassword"]

# def test_reg_request():
#     request_str = b'POST /login HTTP/1.1\r\nHost: localhost:8080\r\nConnection: keep-alive\r\n\r\n' \
#                   b'username_reg=existinguser&password_reg=existingpassword'
#     request = Request(request_str)
#     result = extract_credentials(request)
#     #print(result)
#     assert result == ["existinguser", "existingpassword"]

# if __name__ == '__main__':
#     # test_regular()
#     # test_empty()
#      test_with_special_chars()
#     # test_malformed_form_data()
#     # test_registration()
#     # test_login()
#     #test_login_request()
