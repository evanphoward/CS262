import socket
from _thread import *
import threading

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

PING = 0
REGISTER = 1
LOGIN = 2
SEND_MSG = 3
LOGOUT = 4

USERS = {}
MESSAGES = {}

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
        return -1

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
            return -1

    # No matching username found. Fail.
    return -1

""" Function to list all accounts """
def list_accounts():
    return USERS

""" Function to send a message from one user to another """
def send_message(sender, receiver, message):
    # Find receiver and queue message
    if receiver in USERS:
        MESSAGES[receiver].append(Message(sender, receiver, message))
        return 0

    # Could not find receiver. Fail.
    return -1

""" Function to receive all messages on behalf of user """
def receive_messages(receiver):
    # Deliver all unread messages
    for message in MESSAGES[receiver]:
        # TODO: well, you'd actually do the delivery. just printing for now lol
        print(message.sender, message.receiver, message.message)

    # All messages have been read. Empty messages for receiver.
    MESSAGES[receiver] = []
    return 0

""" Function to delete account """
def delete_account(username):
    # Return messages to sender to notify not delievered
    for message in MESSAGES[username]:
        # TODO: once again, you'd actually have to do the delivery. just printing lol
        print(message.sender, message.receiver, message.message)

    # Delete Account
    del MESSAGES[username]
    del USERS[username]

def unit_tests():
    # TODO: Translate these to units tests and add asserts or some other framework to check responses
    print(USERS)
    create_account("yejoo", "0104")
    print(USERS)
    create_account("yejoo", "0123")
    print(USERS)
    create_account("idk", "sth")
    print(list_accounts())
    print(MESSAGES)

    print(login("yejoo", "0123"))
    print(login("yejoo", "0104"))
    print(login("idk", "sth"))

    send_message("yejoo", "idk", "secrete")
    send_message("yejoo", "idk", "dfjopadd")
    send_message("idk", "yejoo", "dofjsoi")
    print(MESSAGES)

    receive_messages("yejoo")
    receive_messages("idk")
    print(MESSAGES)

    send_message("yejoo", "idk", "more")
    send_message("yejoo", "idk", "more2")
    delete_account("idk")
    print(MESSAGES, USERS)

def pack_msg(msg_str):
    byte_msg = msg_str.encode()
    assert(len(byte_msg) < 256)
    return (len(byte_msg)).to_bytes(1, byteorder='big') + byte_msg

def handle_connection(conn):
    while True:
        data = conn.recv(1024)
        if not data:
            break
        # TODO: Parse data according to wire protocol and do right thing
        opcode = data[0]
        if opcode == PING:
            conn.sendall((0).to_bytes(1, byteorder='big') + pack_msg("PONG!"))
        elif opcode == LOGIN:
            conn.sendall((0).to_bytes(1, byteorder='big') + pack_msg("Successfully Logged In!"))
        elif opcode == REGISTER:
            conn.sendall((0).to_bytes(1, byteorder='big') + pack_msg("Successfully Registered!"))
        elif opcode == SEND_MSG:
            conn.sendall((0).to_bytes(1, byteorder='big') + pack_msg("Successfully Sent Message!"))
        elif opcode == LOGOUT:
            conn.sendall((0).to_bytes(1, byteorder='big') + pack_msg("Logout Acknowledged!"))
            break
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
