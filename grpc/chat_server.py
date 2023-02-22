from concurrent import futures
import grpc
import chat_pb2_grpc
import chat_pb2
import fnmatch

HOST = "127.0.0.1"
PORT = 65432

USERS = {}
LOGGED_IN = set()
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
    LOGGED_IN.add(username)
    return 0

""" Function to log in """
def login(username, password):
    if username in USERS:
        # If there is a matching username, either log them in or fail based on password
        if USERS[username].password == hash(password):
            LOGGED_IN.add(username)
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
        # Do something
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

""" Unit Tests """
def unit_tests():
    # Test: Successfully creates account in USERS
    create_account("yejoo", "0104")
    assert(USERS["yejoo"].username == "yejoo")
    assert(USERS["yejoo"].password == hash("0104"))

    # Test: Username must be unique
    create_account("yejoo", "0123")
    assert(USERS["yejoo"].username == "yejoo")
    assert(USERS["yejoo"].password == hash("0104"))

    # Test: Listing Accounts
    create_account("idk", "sth")
    create_account("yej", "password")
    create_account("middle", "mid")
    assert(list_accounts("*") == "yejoo\nidk\nyej\nmiddle\n")
    assert(list_accounts("ye*") == "yejoo\nyej\n")
    assert(list_accounts("*oo") == "yejoo\n")
    assert(list_accounts("*d*") == "idk\nmiddle\n")

    # Test: Login only logs in users with correct passwords
    assert(login("yejoo", "0123") == 1)
    assert(login("yejoo", "0104") == 0)
    assert(login("idk", "sth") == 0)
    assert(login("dklfjsk;", "sdl k") == 2)
    assert(login("middle", "idk") == 1)

    # Test: sending message queues message
    send_message("yejoo", "idk", "secrete")
    send_message("yejoo", "idk", "dfjopadd")
    send_message("idk", "yejoo", "dofjsoi")
    assert(len(MESSAGES["idk"]) == 2)
    assert(MESSAGES["idk"][0].sender == "yejoo")
    assert(MESSAGES["idk"][0].receiver == "idk")
    assert(MESSAGES["idk"][0].message == "secrete")
    assert(MESSAGES["idk"][1].sender == "yejoo")
    assert(MESSAGES["idk"][1].receiver == "idk")
    assert(MESSAGES["idk"][1].message == "dfjopadd")
    assert(len(MESSAGES["yejoo"]) == 1)
    assert(MESSAGES["yejoo"][0].sender == "idk")
    assert(MESSAGES["yejoo"][0].receiver == "yejoo")
    assert(MESSAGES["yejoo"][0].message == "dofjsoi")

    # Test: receiving message looks at queued message
    assert(receive_messages("yejoo") == "From idk: dofjsoi\n")
    assert(receive_messages("idk") == "From yejoo: secrete\nFrom yejoo: dfjopadd\n")

    # Test: messages are received just once.
    assert(receive_messages("yejoo") == "")
    assert(receive_messages("idk") == "")

    # Test: deleted account returns messages and gets rid of user
    send_message("yejoo", "idk", "more")
    send_message("yejoo", "idk", "more2")
    delete_account("idk")
    assert("idk" not in USERS)
    assert("idk" not in MESSAGES)
    assert(receive_messages("yejoo") == "")

class ChatServerServicer(chat_pb2_grpc.ChatServerServicer):
    def Ping(self, request, context):
        return chat_pb2.Response(retType=SUCCESS, responseString="PONG!")

    def Login(self, request, context):
        login_status = login(request.username, request.password)

        if login_status == 0:
            return chat_pb2.Response(retType=SUCCESS, responseString="Successfully Logged In!")
        elif login_status == 1:
            return chat_pb2.Response(retType=RETRY_ERROR, responseString="Incorrect Password")
        elif login_status == 2:
            return chat_pb2.Response(retType=RETRY_ERROR, responseString="Username Not Found")

    def Register(self, request, context):
        register_status = create_account(request.username, request.password)
        if register_status == 0:
            return chat_pb2.Response(retType=SUCCESS, responseString="Successfully Registered!")
        elif register_status == 1:
            return chat_pb2.Response(retType=RETRY_ERROR, responseString="Username Already Exists")

    def Logout(self, request, context):
        LOGGED_IN.remove(request.username)
        return chat_pb2.Response(retType=SUCCESS, responseString="Logout Acknowledged!")

    def SendMsg(self, request, context):
        send_status = send_message(request.sender, request.receiver, request.message)
        if send_status == 0:
            return chat_pb2.Response(retType=SUCCESS, responseString="Successfully Sent Message!")
        elif send_status == 1:
            return chat_pb2.Response(retType=RETRY_ERROR, responseString="Receiver Username Does Not Exist")

    def List(self, request, context):
        return chat_pb2.Response(retType=SUCCESS, responseString=list_accounts(request.query))

    def Delete(self, request, context):
        delete_account(request.username)
        return chat_pb2.Response(retType=SUCCESS, responseString="Deleted Account")

    def GetMsgs(self, request, context):
        while request.username in LOGGED_IN:
            if MESSAGES[request.username]:
                for msg in MESSAGES[request.username]:
                    yield chat_pb2.Message(sender = msg.sender, receiver = msg.receiver, message = msg.message)
                MESSAGES[request.username] = []

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers = 10))
    chat_pb2_grpc.add_ChatServerServicer_to_server(ChatServerServicer(), server)
    # server.add_insecure_port('[::]:65432')
    server.add_insecure_port(HOST + ":" + str(PORT))
    server.start()
    server.wait_for_termination()

# Comment out serve() and uncomment unit_tests() in order to run unit tests on server functionality
serve()
# unit_tests()
