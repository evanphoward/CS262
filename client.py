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
NUM_ARGUMENTS = {PING: 0, REGISTER: 2, LOGIN: 2, SEND_MSG: 3, LOGOUT: 1, LIST: 1, DELETE: 1}
REQUEST_ERRS = {PING: [], 
                REGISTER: ["Error: Username must be less than 256 characters", "Error: Password must be less than 256 characters"],
                LOGIN:["Error: Username must be less than 256 characters", "Error: Password must be less than 256 characters"],
                SEND_MSG: ["Error: Sender username too long, how did you mess up your own name?", "Error: Recepient Username must be less than 256 characters",  
                            "Error: Message must be less than 256 characters"],
                LOGOUT: ["Error: Username must be less than 256 characters"]}

PRINT_LOCK = threading.Lock()
WAITING_FOR_RESP = False

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
    msg_length = int(resp[1])
    return ret_type, resp[2 : 2 + msg_length].decode()

""" Packs a string argument into a bytes object (appends the length of the string to the front and turns everything into bytes) """
def pack_arg(arg):
    byte_arg = arg.encode()
    if len(arg) >= 256:
        return 2, "Argument too long"
    return 0, (len(byte_arg)).to_bytes(1, byteorder='big') + byte_arg

""" Makes a request to the s socket. req_type is the type of request and args are the arguments needed for that request """
def make_request(s, req_type, args):
    global WAITING_FOR_RESP
    packed_req = (req_type).to_bytes(1, byteorder='big')
    for i, arg in enumerate(args):
        err, packed_arg = pack_arg(arg)
        if err != 0:
            return 2, REQUEST_ERRS[req_type][i]
        packed_req += packed_arg
    s.sendall(packed_req)
    WAITING_FOR_RESP = True
    return 0, ""

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
    err, msg, u = login(s) if resp == "L" else register(s)
    if err != 0:
        return err, msg
    return parse_response(s.recv(1024)) + (u,)

def logout(s):
    make_request(s, LOGOUT, ())
    s.close()

def ping(s):
    err = make_request(s, PING, ())
    if err != 0:
        exit()

def list_users(s):
    search = input("Please supply a search term (Leave blank to see all users, use * as a wildcard)\n")
    return make_request(s, LIST, (search))

def send_msg(s, user):
    receiver = input("Who would you like to send a message to? ")
    msg = input("Please type your message (Max 256 characters)\n")
    return make_request(s, SEND_MSG, (user, receiver, msg))

def delete_account(s, user):
    make_request(s, DELETE, (user,))
    s.close()

def listen_for_resp(s):
    global WAITING_FOR_RESP
    while True:
        try:
            err, ret_msg = parse_response(s.recv(1024))
        except:
            break

        if err == CONNECTION_ERROR:
            print("Connection to server lost, logging out")
            s.close()
            break
        PRINT_LOCK.acquire()
        WAITING_FOR_RESP = False
        print(ret_msg)
        PRINT_LOCK.release()

def main():
    global WAITING_FOR_RESP

    err, s = get_socket()
    if err != 0:
        print(s)
        exit()

    err, msg, username = login_or_register(s)
    print(msg)
    if err == CONNECTION_ERROR:
        exit()
    while err == RETRY_ERROR:
        err, msg, username = login_or_register(s)
        print(msg)
        if err == CONNECTION_ERROR:
            exit()
    WAITING_FOR_RESP = False

    t = threading.Thread(target=listen_for_resp, args=(s,))
    t.daemon = True
    t.start()

    while True:
        while WAITING_FOR_RESP:
            pass
        PRINT_LOCK.acquire()
        opt = print("Welcome " + username + "! Would you like to (L)ist users, (S)end a message, (D)elete your account, or L(o)gout?")
        PRINT_LOCK.release()
        opt = input("").upper()

        PRINT_LOCK.acquire()
        while opt not in "LSDO":
            opt = input("Input not recognized, please type L, S, D, or O. ").upper()
        if opt == "L":
            list_users(s)
        elif opt == "S":
            send_msg(s, username)
        elif opt == "D":
            delete_account(s, username)
            break
        elif opt == "O":
            logout(s)
            break
        PRINT_LOCK.release()
    
main()
