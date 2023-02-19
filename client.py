import socket

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 65432  # The port used by the server

PING = 0
REGISTER = 1
LOGIN = 2
SEND_MSG = 3
LOGOUT = 4

CONNECTION_ERROR = 1
RETRY_ERROR = 2

""" Obtain open socket connection with the server """
def get_socket():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((HOST, PORT))
        return 0, s
    except ConnectionRefusedError:
        return 1, "Connection Refused Error: Server not running or address not accessible"
    except TimeoutError:
        return 1, "Timeout Error: Connection to server timed out"
    except:
        return 1, "Error: Server connection error"

""" Gets a response from server and parses it according to wire protocol """
def parse_response(resp):
    if not resp:
        return 1, "Error: Could not reach server"
    ret_type = resp[0]
    if ret_type != 0:
        err_msg_length = int(resp[1])
        return -1, resp[2:2+err_msg_length]
    msg_length = int(resp[1])
    return 0, resp[2: 2 + msg_length].decode()

""" Packs a string argument into a bytes object (appends the length of the string to the front and turns everything into bytes) """
def pack_arg(arg):
    byte_arg = arg.encode()
    if len(arg) >= 256:
        return 2, "Argument too long"
    return 0, (len(byte_arg)).to_bytes(1, byteorder='big') + byte_arg

""" Makes a request to the s socket. req_type is the type of request and args are the arguments needed for that request """
def make_request(s, req_type, args):
    pack_req_type = (req_type).to_bytes(1, byteorder='big')
    if req_type == PING or req_type == LOGOUT:
        s.sendall(pack_req_type)
    elif req_type == LOGIN or req_type == REGISTER:
        username, password = args
        err, packed_username = pack_arg(username)
        if err != 0:
            return 2, "Error: Username must be less than 256 characters"
        err, packed_password = pack_arg(password)
        if err != 0:
            return 2, "Error: Username must be less than 256 characters"
        s.sendall(pack_req_type + packed_username + packed_password)
    elif req_type == SEND_MSG:
        sender, receiver, msg = args
        err, packed_sender = pack_arg(sender)
        if err != 0:
            return 2, "Error: Sender username too long, how did you mess up your own name?"
        err, packed_sender = pack_arg(sender)
        if err != 0:
            return 2, "Error: Recepient username not found"
        err, packed_msg = pack_arg(msg)
        if err != 0:
            return 2, "Error: Message must be less than 256 characters"
        s.sendall(pack_req_type + packed_sender + packed_receiver + packed_msg)
    err, ret_msg = parse_response(s.recv(1024))
    print(ret_msg)
    return err

def login(s):
    u = input("Username? ")
    p = input("Password? ")
    return make_request(s, LOGIN, (u, p))

def register(s):
    u = input("Username? ")
    p = input("Password? ")
    return make_request(s, REGISTER, (u, p))

def login_or_register(s):
    print("Welcome! Please type `L` to login to an existing account or `R` to register a different account")
    resp = input("")
    while resp not in "LR":
        resp = input("Input not recognized")
    return login(s) if resp == "L" else register(s)

def logout(s):
    make_request(s, LOGOUT, ())
    s.close()

def ping(s):
    err = make_request(s, PING, ())
    if err != 0:
        exit()

def main():
    err, s = get_socket()
    if err != 0:
        print(s)
        exit()
    err = login_or_register(s)
    if err == CONNECTION_ERROR:
        exit()
    while err == RETRY_ERROR:
        err = login_or_register(s)
        if err == CONNECTION_ERROR:
            exit()
    ping(s)
    logout(s)
    # TODO: Server should send all queued messages and client should display them whenever a user logs in
    # TODO: Receive messages on demand while logged in. Some kind of s.recv() in a loop, but also able to send messages whenever the user wants while in this loop
    
main()
