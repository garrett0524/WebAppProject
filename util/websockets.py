import hashlib
import base64
# Write a function named compute_accept that takes a WebSocket key as a parameter (As a string) and returns the correct accept (As a string) according to the WebSocket handshake.

# The output must be character for character exactly what is expected. Make sure you don't have any extra characters in your output (Not even white space).

# You may use libraries to compute the SHA1 hash and Base64 encoding.

def compute_accept(socket_key):
    #string to append to socket key
    guid_string = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
    #encode both strings and concat them
    key_with_guid = socket_key.encode('utf-8') + guid_string.encode('utf-8')
    #sha1 hash the concated str and digest to get raw bytes
    sha1_hash = hashlib.sha1(key_with_guid).digest()
    #base64 encode the sha1 hash and decode to str
    accept_key = base64.b64encode(sha1_hash).decode('utf-8')

    #return final key
    return accept_key



# Write a function named parse_ws_frame that takes bytes as a parameter that represents the bytes of a WebSocket frame and parses all the values of the frame. 
#The function returns an object containing the following fields (You have some freedom in how you design the class for this object as long as it has the required fields).

# fin_bit 
# An int with the value of the fin bit (Either 1 or 0)
# opcode
# An int with the value of the opcode (eg. if the op code is bx1000, this field stores 8 as an int)
# payload_length
# The payload length as an int. Your function must handle all 3 payload length modes
# payload
# The unmasked bytes of the payload

class parsed_frame:
    def __init__(self, fin_bit, opcode, payload_length,payload,masking_key):
        ## An int with the value of the fin bit (Either 1 or 0)
        self.fin_bit = fin_bit
        ## An int with the value of the opcode (eg. if the op code is bx1000, this field stores 8 as an int)
        self.opcode = opcode
        ## The payload length as an int. Your function must handle all 3 payload length modes
        self.payload_length = payload_length
        ## The unmasked bytes of the payload
        self.payload = payload
        
        self.masking_key = masking_key

    

def parse_ws_frame(socketframe_bytes):
        #set fin bit to 0 and enter while before actually calculating the fin bit, this way if the fin bit IS 1, we still parse the final frame
        #fin_bit = 0
        #while fin_bit == 0:
        print('finbit == 0, initiating parse_ws_frame')

        #get the first byte of the socketframe_bytes to get the first byte (8bits), mask to only get the first bit
        fin_bit = socketframe_bytes[0] & 0b10000000
        if fin_bit == 0b10000000:
            fin_bit = 1
        else:
            fin_bit = 0
    
        #mask to only get bits 4,5,6,7
        opcode = (socketframe_bytes[0] & 0b00001111) 
        
        payload_length = socketframe_bytes[1] & 0b01111111
        if payload_length < 126:
            new_payload_length = payload_length
            #masking key is bytes 2,3,4,5
            masking_key = ((socketframe_bytes[2] << 24) | (socketframe_bytes[3] << 16) |
                    (socketframe_bytes[4] << 8) | socketframe_bytes[5])
            #location that the payload begins
            payload_starts = 6

        elif payload_length ==126:
            new_payload_length = ((socketframe_bytes[2] << 8) | socketframe_bytes[3]) #bitshift byte 2 eight bits to the left, and then or with byte 3
            #masking key is bytes 4,5,6,7
            masking_key = ((socketframe_bytes[4] << 24) | (socketframe_bytes[5] << 16) |
                    (socketframe_bytes[6] << 8) | socketframe_bytes[7])
            payload_starts = 8
            
        elif payload_length ==127:
            new_payload_length  = (
                (socketframe_bytes[2] << 56) | (socketframe_bytes[3] << 48) |
                (socketframe_bytes[4] << 40) | (socketframe_bytes[5] << 32) |
                (socketframe_bytes[6] << 24) | (socketframe_bytes[7] << 16) |
                (socketframe_bytes[8] << 8) | socketframe_bytes[9]
                )
            #masking key is bytes 10,11,12,13
            masking_key = ((socketframe_bytes[10] << 24) | (socketframe_bytes[11] << 16) |
                    (socketframe_bytes[12] << 8) | socketframe_bytes[13])
            payload_starts = 14
        
        masking_key_bytes = masking_key.to_bytes(4, byteorder='big')
        payload = bytearray()                                                #Create new empty byte array

        while len(payload) < new_payload_length:                            #add the socketframe starts byte to the empty payload byte array
            #print('parse while loop')
            try:
                next_byte = socketframe_bytes[payload_starts].to_bytes(1, byteorder='big')
            except IndexError:
                #print('payload loop broken')
                break

            payload += next_byte
            payload_starts +=1
        

        for byte in range(len(payload)):      #changing to len(payload) to avoid infinite loop
            #print('unmask loop')
            payload[byte] = payload[byte] ^ masking_key_bytes[byte % 4]
            
        return parsed_frame(fin_bit, opcode, new_payload_length, payload,masking_key_bytes)






    #Write a function named generate_ws_frame that takes bytes as a parameter and returns a properly formatted WebSocket frame (As bytes) 
    # with the input bytes as its payload. Use a fin bit of 1, an op code of bx0001 for text, and no mask. You need to handle all 3 payload length modes.

def generate_ws_frame(input_bytes):
        fin_bit = 1
        opcode = 0b0001

        byte0 = (fin_bit <<7) | opcode #shift fin bit back 7 and or with opcode to get first byte

        payload_length = len(input_bytes) 

        #print('length within function',payload_length)
        
        if payload_length < 126:
            byte1 = payload_length.to_bytes(1, byteorder='big')
            headers = byte0.to_bytes(1,byteorder='big') + byte1
            
        
        elif payload_length <= 65535:
            byte1 = 126  #binary representation of 126

            bytes2_and_3 = payload_length.to_bytes(2,byteorder='big')

            headers = byte0.to_bytes(1,byteorder='big') + byte1.to_bytes(1,byteorder='big') + bytes2_and_3


        else:
            byte1 = 127

            bytes_2_to_9 = payload_length.to_bytes(8,byteorder='big')

            headers = byte0.to_bytes(1,byteorder='big') + byte1.to_bytes(1,byteorder='big') + bytes_2_to_9


        complete_payload = headers + input_bytes




        #socket_frame = b""

        #return socket_frame
        return complete_payload
    




#def test_parse_frame_4b_payload():
    # test_frame = bytes([0b10000000, 0b10000100, 0b10101100, 0b01100100, 0b00100100, 0b00100100,0b01101010,0b01000110,0b01010101,0b10101010])  # "TEST"
    # parsed = parse_ws_frame(test_frame)
    # print(parsed.opcode)

#     assert parsed.fin_bit == 1
#     assert parsed.opcode == 0
#     assert parsed.payload_length == 4
   
#     #assert parsed.payload == unmasked_payload
#     #print(bytes([0b10101100, 0b01100100, 0b00100100, 0b00100100]))
#     # 11000110, 00100010, 01110001, 10001110
#     #print(bytes(0b11000110, 0b00100010, 0b01110001, 0b10001110))
#     #print('parsed payload',parsed.payload)
#     binary_payload = ''.join(format(byte, '08b') for byte in parsed.payload)

#     #print(parsed.payload)
#     assert(binary_payload == '11000110001000100111000110001110')
#     print('All Parse Tests Pass!')

# def test_generate_ws_frame_small():
#     input_bytes = 0b01101010010001100101010110101010.to_bytes(4,byteorder='big')
#     output = (generate_ws_frame(input_bytes))
#     #print('generate',output)
#     binary_output = ''.join(format(byte, '08b') for byte in output)
#     assert(binary_output == '100000010000010001101010010001100101010110101010')
#     print('Small Generate Tests pass!')

# def test_generate_ws_frame_medium():
#     # Sample payload between 126 and 65535 bytes
#     input_bytes = 0b01101010010001100101010110101010.to_bytes(4,byteorder='big') * 32
#     output = (generate_ws_frame(input_bytes))
#     expected_payload_length = len(input_bytes)
#     print('expected payload length',expected_payload_length)

#     expected_fin_opcode = 0b10000001 
#     expected_payload_length_indicator = 126
#     expected_payload_length_bytes = expected_payload_length.to_bytes(2, byteorder='big')

#     generated_frame = generate_ws_frame(input_bytes)

#     assert generated_frame[0] == expected_fin_opcode
#     print('frame one',generated_frame[1])
#     binary_output = ''.join(format(generated_frame[1], '08b'))
#     print('binary output',binary_output)

#     assert generated_frame[1] == expected_payload_length_indicator
#     assert generated_frame[2:4] == expected_payload_length_bytes
#     assert generated_frame[4:] == input_bytes 
#     print('Medium Generate Tests Pass!')



     
# if __name__ == '__main__':
#        test_parse_frame_4b_payload()
#       test_generate_ws_frame_small()
#       test_generate_ws_frame_medium()



      