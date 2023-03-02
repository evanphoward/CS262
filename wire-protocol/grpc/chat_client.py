import grpc
import chat_pb2_grpc
import chat_pb2
from _thread import *
import threading

HOST = "127.0.0.1"
PORT = 65432

SUCCESS = 0
CONNECTION_ERROR = 1
RETRY_ERROR = 2
MESSAGE = 3

RECEIVED_MESSAGES = []

def login(stub):
    u = input("Username? ")
    p = input("Password? ")
    user = chat_pb2.User(username = u, password = p)
    return stub.Login(user), u

def register(stub):
    u = input("Username? ")
    p = input("Password? ")
    user = chat_pb2.User(username = u, password = p)
    return stub.Register(user), u

def login_or_register(stub):
    resp = input("Welcome! Would you like to (L)ogin to an existing account or (R)egister a new account (Type L or R)?\n").upper()
    while resp not in "LR":
        resp = input("Input not recognized, please type L or R. ").upper()
    return login(stub) if resp == "L" else register(stub)

def list_users(stub):
    search = input("Please supply a search term (Leave blank to see all users, use * as a wildcard)\n")
    # Blank Input by User
    if not search:
        search = "*"
    query = chat_pb2.ListQuery(query = search)
    return stub.List(query)

def send_msg(stub, user):
    receiver = input("Who would you like to send a message to? ")
    msg = input("Please type your message (Max 256 characters)\n")
    msg_obj = chat_pb2.Message(sender = user, receiver = receiver, message = msg)
    return stub.SendMsg(msg_obj)

def receive_msgs(msg_iterator):
    global RECEIVED_MESSAGES
    try:
        for msg in msg_iterator:
            RECEIVED_MESSAGES.append("From " + msg.sender + ": " + msg.message + "\n")
    except Exception:
        # Exception may happen when channel closes upon logging out, we just want this thread to exit
        return

def run():
    global RECEIVED_MESSAGES
    with grpc.insecure_channel(HOST + ":" + str(PORT)) as channel:
        stub = chat_pb2_grpc.ChatServerStub(channel)

        # on connection, user must login or register
        response, username = login_or_register(stub)
        print(response.responseString)
        if response.retType == CONNECTION_ERROR:
            exit()
        while response.retType == RETRY_ERROR:
            response, username = login_or_register(stub)
            print(response.responseString)
            if response.retType == CONNECTION_ERROR:
                exit()

        start_new_thread(receive_msgs, (stub.GetMsgs(chat_pb2.Username(username = username)),))

        # once logged in, user can use full functionality of app
        while True:
            opt = print("Welcome " + username + "! Would you like to (C)heck messages, (L)ist users, (S)end a message, (D)elete your account, or L(o)gout?")
            opt = input("").upper()

            while opt not in "CLSDO":
                opt = input("Input not recognized, please type C, L, S, D, or O. ").upper()

            # Check messages
            if opt == "C":
                if RECEIVED_MESSAGES:
                    print("New Messages:")
                    print(''.join(RECEIVED_MESSAGES))
                else:
                    print("No New Messages!")
                RECEIVED_MESSAGES = []

            # List users on the app
            elif opt == "L":
                response = list_users(stub)
                print(response.responseString)
                if response.retType == CONNECTION_ERROR:
                    break

            # Send message to another user
            elif opt == "S":
                response = send_msg(stub, username)
                print(response.responseString)
                if response.retType == CONNECTION_ERROR:
                    break

            # Delete user's own account
            elif opt == "D":
                response = stub.Delete(chat_pb2.Username(username = username))
                if RECEIVED_MESSAGES:
                    print("Before you go, here are your new messages:")
                    print(''.join(RECEIVED_MESSAGES))
                print(response.responseString)
                break

            # Log out
            elif opt == "O":
                response = stub.Logout(chat_pb2.Username(username = username))
                if RECEIVED_MESSAGES:
                    print("Before you go, here are your new messages:")
                    print(''.join(RECEIVED_MESSAGES))
                print(response.responseString)
                break

run()
