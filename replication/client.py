import socket

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 65432  # The port used by the server

# Connection Codes
SERVER = 0
CLIENT = 1

# Operation Codes
PING = 0
REGISTER = 1
LOGIN = 2
SEND_MSG = 3
LOGOUT = 4
LIST = 5
DELETE = 6

# Response Codes
CONNECTION_ERROR = 1
RETRY_ERROR = 2
MESSAGE = 3

class Client():
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    """ Makes a request to the socket. req_type is the type of request and args are the arguments needed for that request """
    def make_request(self, req_type, args):
        """ Gets a response from server and parses it according to wire protocol """
        def parse_response(resp):
            if not resp:
                return [CONNECTION_ERROR, "Error: Lost connection to server"]
            i = 0
            responses = []
            while i < len(resp):
                ret_type = resp[i]
                msg_length = int(resp[i + 1])
                responses.append((ret_type, resp[i + 2 : i + 2 + msg_length].decode()))
                i += 2 + msg_length
            return responses

        """ Packs a string argument into a bytes object (appends the length of the string to the front and turns everything into bytes) """
        def pack_arg(arg):
            byte_arg = arg.encode()
            if len(arg) >= 256:
                return 2, "Argument too long"
            return 0, (len(byte_arg)).to_bytes(1, byteorder='big') + byte_arg

        packed_req = (req_type).to_bytes(1, byteorder='big') + (len(args)).to_bytes(1, byteorder='big')

        # Pack each argument into a bytes array and append them together to send to the server
        for i, arg in enumerate(args):
            err, packed_arg = pack_arg(arg)
            if err != 0:
                return RETRY_ERROR, REQUEST_ERRS[req_type][i]
            packed_req += packed_arg
        try:
            self.socket.sendall(packed_req)
        except:
            return CONNECTION_ERROR, "Error: Lost connection to server"

        # Get parsed responses from the server
        responses = parse_response(self.socket.recv(1024))
        # If all of the responses are messages for the user, keep waiting until we get the response to this request
        while all(resp[0] == MESSAGE for resp in responses):
            responses.extend(parse_response(self.socket.recv(1024)))

        # Print all the messages to the user, and return the response to this request
        ret = responses[0]
        if len(responses) > 1:
            for resp in responses:
                if resp[0] == MESSAGE:
                    RECEIVED_MESSAGES.append(resp[1])
                else:
                    ret = resp
        return ret

    def login(self):
        u = input("Username? ")
        p = input("Password? ")
        return self.make_request(LOGIN, (u, p)) + (u,)

    def register(self):
        u = input("Username? ")
        p = input("Password? ")
        return self.make_request(REGISTER, (u, p)) + (u,)

    def login_or_register(self):
        resp = input("Welcome! Would you like to (L)ogin to an existing account or (R)egister a new account (Type L or R)?\n").upper()
        while resp not in "LR":
            resp = input("Input not recognized, please type L or R. ").upper()
        return self.login() if resp == "L" else self.register()

    def run(self):
        # Create socket for connection and send connection message to server
        self.socket.connect((HOST, PORT))
        connection_message = (CLIENT).to_bytes(1, byteorder = 'big')
        self.socket.sendall(connection_message)

        # on connection, user must login or register
        err, msg, username = self.login_or_register()
        print(msg)
        if err == CONNECTION_ERROR:
            exit()
        while err == RETRY_ERROR:
            err, msg, username = self.login_or_register()
            print(msg)
            if err == CONNECTION_ERROR:
                exit()
def main():
    client = Client()
    client.run()

main()
