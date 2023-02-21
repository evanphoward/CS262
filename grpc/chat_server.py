import grpc
import chat_pb2_grpc
import chat_pb2

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

USERS = {}
MESSAGES = {}

SUCCESS = 0
CONNECTION_ERROR = 1
RETRY_ERROR = 2
MESSAGE = 3

""" Class that represents a User of the application """
class User():
    def __init__(self, username, password):
        self.username = username
        self.password = hash(password)
        self.socket = None

""" Class that represents a Message on the application """
class Message():
    def __init__(self, sender, receiver, message):
        self.sender = sender
        self.receiver = receiver
        self.message = message

""" Function to create a new account """
def create_account(username, password):
    # Fails if username is not unique
    if username in USERS:
        return 1

    # Appends account to list of users otherwise
    USERS[username] = User(username, password)
    MESSAGES[username] = []
    return 0

""" Function to log in """
def login(username, password):
    if username in USERS:
        # If there is a matching username, either log them in or fail based on password
        if USERS[username].password == hash(password):
            return 0
        else:
            return 1

    # No matching username found. Fail.
    return 2

""" Function to search and list all accounts """
def list_accounts(search):
    accounts = ""
    for username in USERS:
        if fnmatch.fnmatch(username, search):
            accounts += username
            accounts += "\n"

    return accounts

""" Function to send a message from one user to another """
def send_message(sender, receiver, message):
    # Find receiver and queue message
    if receiver in USERS:
        if USERS[receiver].socket:
            USERS[receiver].socket.sendall((MESSAGE).to_bytes(1, byteorder='big') + pack_msg("From " + sender + ": " + message + "\n"))
        else:
            MESSAGES[receiver].append(Message(sender, receiver, message))
        return 0

    # Could not find receiver. Fail.
    return 1

""" Function to receive all messages on behalf of user """
def receive_messages(receiver):
    # Deliver all unread messages
    deliver = ""
    for message in MESSAGES[receiver]:
        deliver += ("From " + message.sender + ": " + message.message + "\n")

    # All messages have been read. Empty messages for receiver.
    MESSAGES[receiver] = []
    return deliver

""" Function to delete account """
def delete_account(username):
    # Delete Account
    del MESSAGES[username]
    del USERS[username]

class ChatServerServicer(chat_pb2_grpc.ChatServerServicer):
    def Ping(self, request, context):
        return chat_pb2_grpc.Response(retType=SUCCESS, responseString="PONG!")

    def Login(self, request, context):
        login_status = login(request.username, request.password)

        if login_status == 0:
            return chat_pb2_grpc.Response(retType=SUCCESS, responseString="Successfully Logged In!")
        elif login_status == 1:
            return chat_pb2_grpc.Response(retType=RETRY_ERROR, responseString="Incorrect Password")
        elif login_status == 2:
            return chat_pb2_grpc.Response(retType=RETRY_ERROR, responseString="Username Not Found")

    def Registered(self, request, context):
        register_status = create_account(request.username, request.password)
        if register_status == 0:
            return chat_pb2_grpc.Response(retType=SUCCESS, responseString="Successfully Registered!")
        elif register_status == 1:
            return chat_pb2_grpc.Response(retType=RETRY_ERROR, responseString="Username Already Exists")

    def Logout(self, request, context):
        return chat_pb2_grpc.Response(retType=SUCCESS, responseString="Logout Acknowledged!")

    def SendMsg(self, request, context):
        return chat_pb2_grpc.Response(retType=SUCCESS, responseString="Successfully Sent Message!")

    def List(self, request, context):
        return chat_pb2_grpc.Response(retType=SUCCESS, responseString=list_accounts(request.query))

    def Delete(self, request, context):
        return chat_pb2_grpc.Response(retType=SUCCESS, responseString="Successfully Sent Message!")
