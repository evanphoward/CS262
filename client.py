import socket

HOST = "10.250.79.111"  # The server's hostname or IP address
PORT = 65432  # The port used by the server

PING = 0
REGISTER = 1
LOGIN = 2
SEND_MSG = 3

# with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#     s.connect((HOST, PORT))
#     s.sendall(b"Hello, world")
#     data = s.recv(1024)

# print(f"Received {data!r}")

""" Obtain open socket connection with the server """
def get_socket():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        return 0, s.connect((HOST, PORT))
    except ConnectionRefusedError:
        return -1, "Connection Refused: Server not running or address not accessible"
    except TimeoutError:
        return -1, "Timeout: Connection to server timed out"
    except:
        return -1, "Error in server connection"

def make_request(s, req_type, args):
    if req_type == PING:
        s.sendall(req_type)
    elif req_type == LOGIN:
        pass
    elif req_type == REGISTER:
        pass
    elif req_type == SEND_MSG:
        pass


def login(s):
    u = input("Username?\n")
    p = input("Password?\n")
    return make_request(s, LOGIN, (u, p))
    pass

def register(s):
    pass

def login_or_register(s):
    print("Welcome! Please type `L` to login to an existing account or `R` to register a different account\n")
    resp = input("")
    while resp not in "LR":
        resp = input("Input not recognized")
    if resp == "L":
        login(s)
    else:
        register(s)
    return

def main():
    err, s = get_socket()
    if err != 0:
        print(s)
        exit()
    login_or_register(s)

main()
