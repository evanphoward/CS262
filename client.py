import socket
from _thread import *
import threading

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 65432  # The port used by the server

PING = 0
REGISTER = 1
LOGIN = 2
SEND_MSG = 3
LOGOUT = 4
LIST = 5
DELETE = 6
NUM_ARGS = {PING: 0, REGISTER: 2, LOGIN: 2, SEND_MSG: 3, LOGOUT: 1, LIST: 1, DELETE: 1}
REQUEST_ERRS = {PING: [],
                REGISTER: ["Error: Username must be less than 256 characters", "Error: Password must be less than 256 characters"],
                LOGIN:["Error: Username must be less than 256 characters", "Error: Password must be less than 256 characters"],
                SEND_MSG: ["Error: Sender username too long, how did you mess up your own name?", "Error: Recepient Username must be less than 256 characters",
                            "Error: Message must be less than 256 characters"],
                LOGOUT: ["Error: Username must be less than 256 characters"]}

CONNECTION_ERROR = 1
RETRY_ERROR = 2
MESSAGE = 3

RECEIVED_MESSAGES = []

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

""" Makes a request to the s socket. req_type is the type of request and args are the arguments needed for that request """
def make_request(s, req_type, args):
    packed_req = (req_type).to_bytes(1, byteorder='big') + (len(args)).to_bytes(1, byteorder='big')

    # Pack each argument into a bytes array and append them together to send to the server
    for i, arg in enumerate(args):
        err, packed_arg = pack_arg(arg)
        if err != 0:
            return RETRY_ERROR, REQUEST_ERRS[req_type][i]
        packed_req += packed_arg
    try:
        s.sendall(packed_req)
    except:
        return CONNECTION_ERROR, "Error: Lost connection to server"

    # Get parsed responses from the server
    responses = parse_response(s.recv(1024))
    # If all of the responses are messages for the user, keep waiting until we get the response to this request
    while all(resp[0] == MESSAGE for resp in responses):
        responses.extend(parse_response(s.recv(1024)))

    # Print all the messages to the user, and return the response to this request
    ret = responses[0]
    if len(responses) > 1:
        for resp in responses:
            if resp[0] == MESSAGE:
                RECEIVED_MESSAGES.append(resp[1])
            else:
                ret = resp
    return ret

def login(s):
    u = input("Username? ")
    p = input("Password? ")
    return make_request(s, LOGIN, (u, p)) + (u,)

def register(s):
    u = input("Username? ")
    p = input("Password? ")
    return make_request(s, REGISTER, (u, p)) + (u,)

def login_or_register(s):
    resp = input("Welcome! Would you like to (L)ogin to an existing account or (R)egister a new account (Type L or R)?\n").upper()
    while resp not in "LR":
        resp = input("Input not recognized, please type L or R. ").upper()
    return login(s) if resp == "L" else register(s)

def logout(s):
    ret = make_request(s, LOGOUT, ())
    s.close()
    return ret

def ping(s):
    return make_request(s, PING, ())

def list_users(s):
    search = input("Please supply a search term (Leave blank to see all users, use * as a wildcard)\n")
    # Blank Input by User
    if not search:
        return make_request(s, LIST, ())
    # User Input
    return make_request(s, LIST, (search,))

def send_msg(s, user):
    receiver = input("Who would you like to send a message to? ")
    msg = input("Please type your message (Max 256 characters)\n")
    return make_request(s, SEND_MSG, (user, receiver, msg))

def delete_account(s, user):
    ret = make_request(s, DELETE, (user,))
    s.close()
    return ret

def main():
    global RECEIVED_MESSAGES

    err, s = get_socket()
    if err != 0:
        print(s)
        exit()

    # on connection, user must login or register
    err, msg, username = login_or_register(s)
    print(msg)
    if err == CONNECTION_ERROR:
        exit()
    while err == RETRY_ERROR:
        err, msg, username = login_or_register(s)
        print(msg)
        if err == CONNECTION_ERROR:
            exit()

    # once logged in, user can use full functionality of the app
    while True:
        opt = print("Welcome " + username + "! Would you like to (C)heck messages, (L)ist users, (S)end a message, (D)elete your account, or L(o)gout?")
        opt = input("").upper()

        while opt not in "CLSDO":
            opt = input("Input not recognized, please type C, L, S, D, or O. ").upper()

        # Check messages
        if opt == "C":
            ping(s)
            if RECEIVED_MESSAGES:
                print("New Messages:")
                print(''.join(RECEIVED_MESSAGES))
            else:
                print("No New Messages!")
            RECEIVED_MESSAGES = []

        # List users on the app
        elif opt == "L":
            err, msg = list_users(s)
            print(msg)
            if err == CONNECTION_ERROR:
                s.close()
                break

        # Send message to another user
        elif opt == "S":
            err, msg = send_msg(s, username)
            print(msg)
            if err == CONNECTION_ERROR:
                s.close()
                break

        # Delete user's own account
        elif opt == "D":
            _, msg = delete_account(s, username)
            if RECEIVED_MESSAGES:
                print("Before you go, here are your new messages:")
                print(''.join(RECEIVED_MESSAGES))
            print(msg)
            break

        # Log out
        elif opt == "O":
            _, msg = logout(s)
            if RECEIVED_MESSAGES:
                print("Before you go, here are your new messages:")
                print(''.join(RECEIVED_MESSAGES))
            print(msg)
            break

main()
