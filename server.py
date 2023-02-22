import socket
from _thread import *
import threading
import fnmatch

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

PING = 0
REGISTER = 1
LOGIN = 2
SEND_MSG = 3
LOGOUT = 4
LIST = 5
DELETE = 6

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
    assert(receive_messages("yejoo") == "From idk: Account Deleted. Original message not delievered: more\nFrom idk: Account Deleted. Original message not delievered: more2\n")
    assert("idk" not in USERS)
    assert("idk" not in MESSAGES)
    assert(receive_messages("yejoo") == "")


def pack_msg(msg_str):
    byte_msg = msg_str.encode()
    assert(len(byte_msg) < 256)
    return (len(byte_msg)).to_bytes(1, byteorder='big') + byte_msg

def parse_request(request):
    opcode = request[0]
    num_args = request[1]
    args = []
    index = 2

    for arg in range(num_args):
        arg_length = int(request[index])
        args.append(request[index + 1: index + 1 + arg_length].decode())
        index = index + arg_length + 1

    return opcode, args

def handle_connection(conn):
    while True:
        data = conn.recv(1024)
        if not data:
            break

        opcode, args = parse_request(data)

        if opcode == PING:
            conn.sendall((SUCCESS).to_bytes(1, byteorder='big') + pack_msg("PONG!"))
        elif opcode == LOGIN:
            # Get login arguments
            username = args[0]
            password = args[1]

            # Login and send success/failure to client
            login_status = login(username, password)
            if login_status == 0:
                USERS[username].socket = conn
                conn.sendall((SUCCESS).to_bytes(1, byteorder='big') + pack_msg("Successfully Logged In!"))
                messages_to_deliver = receive_messages(username)
                if messages_to_deliver:
                    conn.sendall((MESSAGE).to_bytes(1, byteorder='big') + pack_msg(messages_to_deliver))
            elif login_status == 1:
                conn.sendall((RETRY_ERROR).to_bytes(1, byteorder='big') + pack_msg("Incorrect Password"))
            elif login_status == 2:
                conn.sendall((RETRY_ERROR).to_bytes(1, byteorder='big') + pack_msg("Username Not Found"))
        elif opcode == REGISTER:
            # Get register arguments
            username = args[0]
            password = args[1]

            # Create account and send success/failure to client
            register_status = create_account(username, password)
            if register_status == 0:
                USERS[username].socket = conn
                conn.sendall((SUCCESS).to_bytes(1, byteorder='big') + pack_msg("Successfully Registered!"))
            elif register_status == 1:
                conn.sendall((RETRY_ERROR).to_bytes(1, byteorder='big') + pack_msg("Username Already Exists"))
        elif opcode == SEND_MSG:
            # Get send arguments
            sender = args[0]
            receiver = args[1]
            message = args[2]

            # Send message and send success/failure to client
            send_status = send_message(sender, receiver, message)
            if send_status == 0:
                conn.sendall((SUCCESS).to_bytes(1, byteorder='big') + pack_msg("Successfully Sent Message!"))
            elif send_status == 1:
                conn.sendall((RETRY_ERROR).to_bytes(1, byteorder='big') + pack_msg("Receiver Username Does Not Exist"))
        elif opcode == LIST:
            # TODO: maybe not use pack_msg on the full thing. if there are lots of users, may fail assert in it.
            if len(args) == 0:
                accounts = list_accounts("*")
            else:
                search = args[0]
                accounts = list_accounts(search)

            conn.sendall((SUCCESS).to_bytes(1, byteorder='big') + pack_msg(accounts))
        elif opcode == LOGOUT:
            USERS[username].socket = None
            conn.sendall((SUCCESS).to_bytes(1, byteorder='big') + pack_msg("Logout Acknowledged!"))
            break
        elif opcode == DELETE:
            username = args[0]
            delete_account(username)
            conn.sendall((SUCCESS).to_bytes(1, byteorder='big') + pack_msg("Deleted Account!"))
            break

    # If we break out of the loop, we close the connection before return from this function
    conn.close()

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    s.bind((HOST, PORT))
    s.listen()

    while True:
        conn, addr = s.accept()
        start_new_thread(handle_connection, (conn,))

    s.close()

main()
# unit_tests()
