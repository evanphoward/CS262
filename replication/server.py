import os
import socket
import pandas as pd
import sys
import fnmatch
from _thread import *
from threading import Timer

# Host IP for Server ID 1, 2, 3
HOSTS = ["127.0.0.1", "127.0.0.1", "127.0.0.1"]
# Port used is PORT + ID
PORT = 65432

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

# Error Codes
SUCCESS = 0
CONNECTION_ERROR = 1
RETRY_ERROR = 2
MESSAGE = 3

# Server Leader Codes
LEADER = 0
FOLLOWER = 1

# Server Alive Codes
ALIVE = 0
DEAD = 1

# Ping interval for server-to-server communication (Change interval as desired)
PING_INTERVAL = 1

""" Class that represents a User of the application """
class User():
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.socket = None
        self.messages = []

    def add_message(self, message):
        self.messages.append(message)

""" Class that represents a Message on the application """
class Message():
    def __init__(self, sender, receiver, message):
        self.sender = sender
        self.receiver = receiver
        self.message = message

""" Class for having a thread that runs the same thing repeatedly"""
class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer     = None
        self.interval   = interval
        self.function   = function
        self.args       = args
        self.kwargs     = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False

""" Class that represents a Server """
class Server():
    """ Initialize Server Object """
    def __init__(self, id):
        # Initialize host and port
        self.id = id
        self.master_id = 0
        self.host = HOSTS[id]
        self.port = PORT + id

        # Create socket
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Create other server sockets
        self.other_servers = {}
        for i in range(self.id):
            self.other_servers[self.master_id + PORT + i] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Create account dictionary and corresponding CSV files
        self.account_path = "server-" + str(self.port) + "-accounts.csv"
        self.message_path = "server-" + str(self.port) + "-messages.csv"

        if os.path.isfile(self.account_path):
            self.accounts = pd.read_csv(self.account_path, dtype = str)
        else:
            self.accounts = pd.DataFrame(columns = ["Username", "Password", "Time"])
            self.accounts.to_csv(self.account_path, index = False)

        if os.path.isfile(self.message_path):
            self.messages = pd.read_csv(self.message_path, dtype = str)
        else:
            self.messages = pd.DataFrame(columns = ["Sender", "Receiver", "Message", "Time"])
            self.messages.to_csv(self.message_path, index = False)

        # Create list of users for this server and parse CSV files
        self.users = {}
        for index, account in self.accounts.iterrows():
            self.users[account["Username"]] = User(account["Username"], account["Password"])
        for index, message in self.messages.iterrows():
            self.users[message["Receiver"]].add_message(Message(message["Sender"], message["Receiver"], message["Message"]))

    """ Function to create a new account """
    # TODO: make sure that self.accounts is fresh before calling create_account
    def create_account(self, username, password):
        # Fails if username is not unique
        if username in self.accounts["Username"].values:
            return 1

        # Appends account to list of users otherwise and updates CSV file
        self.users[username] = User(username, password)
        self.accounts.loc[len(self.accounts)] = [username, self.users[username].password, pd.Timestamp.now()]
        self.accounts.to_csv(self.account_path, index = False)
        return 0

    """ Function to log in """
    def login(self, username, password):
        if username in self.users:
            # If there is a matching username, either log them in or fail based on password
            if self.users[username].password == password:
                return 0
            else:
                return 1

        # No matching username found. Fail.
        return 2

    """ Function to search and list all accounts """
    def list_accounts(self, search):
        accounts = []
        # Find all matching usernames
        for username in self.users:
            if fnmatch.fnmatch(username, search):
                accounts.append(username)

        return accounts

    """ Function to queue a message from one user to another """
    def send_message(self, sender, receiver, message):
        match_username = self.accounts.loc[self.accounts["Username"] == receiver]

        # No matching receiver found. Fail.
        if len(match_username) == 0:
            return 1

        # Queue message
        # TODO: queueing all "sent" messages. should have another function deal with receiving messages instantly if logged in
        self.users[receiver].add_message(Message(sender, receiver, message))
        self.messages.loc[len(self.messages)] = [sender, receiver, message, pd.Timestamp.now()]
        self.messages.to_csv(self.message_path, index = False)
        return 0

    """ Function to receive all messages on behalf of user """
    def receive_messages(self, receiver):
        # Deliver all unread messages
        to_deliver = ""
        for message in self.users[receiver].messages:
            to_deliver += ("From " + message.sender + ": " + message.message + "\n")

        # Delete messages
        self.messages = self.messages[self.messages["Receiver"] != receiver]
        self.messages.to_csv(self.message_path, index = False)
        self.users[receiver].messages = []
        return to_deliver

    """ Function to delete account """
    def delete_account(self, username):
        # Delete Account
        # TODO: add handling of messages to be received by deleted user
        self.accounts = self.accounts[self.accounts["Username"] != username]
        self.accounts.to_csv(self.account_path, index = False)
        self.messages = self.messages[self.messages["Receiver"] != username]
        self.messages.to_csv(self.message_path, index = False)
        del self.users[username]

        return

    """ Function that handles connection with another server """
    def handle_server_connection(self, conn, port):
        self.other_servers[port] = conn
        print("Connected to " + str(port))

    """ Function that handles connection with client """
    def handle_client_connection(self, conn):
        """ Function to take a message string and encode it into bytes """
        def pack_msg(msg_str):
            byte_msg = msg_str.encode()
            assert(len(byte_msg) < 256)
            return (len(byte_msg)).to_bytes(1, byteorder='big') + byte_msg

        """ Function to parse request from client """
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

        while True:
            data = conn.recv(1024)
            if not data:
                break

            opcode, args = parse_request(data)

            # Handle request from client based on operation
            # Ping
            if opcode == PING:
                conn.sendall((SUCCESS).to_bytes(1, byteorder='big') + pack_msg("PONG!"))

            # Login
            elif opcode == LOGIN:
                # Get login arguments
                username = args[0]
                password = args[1]

                # Login and send success/failure to client
                login_status = self.login(username, password)
                if login_status == 0:
                    self.users[username].socket = conn
                    conn.sendall((SUCCESS).to_bytes(1, byteorder='big') + pack_msg("Successfully Logged In!"))
                    messages_to_deliver = self.receive_messages(username)
                    if messages_to_deliver:
                        conn.sendall((MESSAGE).to_bytes(1, byteorder='big') + pack_msg(messages_to_deliver))
                elif login_status == 1:
                    conn.sendall((RETRY_ERROR).to_bytes(1, byteorder='big') + pack_msg("Incorrect Password"))
                elif login_status == 2:
                    conn.sendall((RETRY_ERROR).to_bytes(1, byteorder='big') + pack_msg("Username Not Found"))

            # Register
            elif opcode == REGISTER:
                # Get register arguments
                username = args[0]
                password = args[1]

                # Create account and send success/failure to client
                register_status = self.create_account(username, password)
                if register_status == 0:
                    self.users[username].socket = conn
                    conn.sendall((SUCCESS).to_bytes(1, byteorder='big') + pack_msg("Successfully Registered!"))
                elif register_status == 1:
                    conn.sendall((RETRY_ERROR).to_bytes(1, byteorder='big') + pack_msg("Username Already Exists"))

            # Send Message
            elif opcode == SEND_MSG:
                # Get send arguments
                sender = args[0]
                receiver = args[1]
                message = args[2]

                # Send message and send success/failure to client
                send_status = self.send_message(sender, receiver, message)
                if send_status == 0:
                    conn.sendall((SUCCESS).to_bytes(1, byteorder='big') + pack_msg("Successfully Sent Message!"))
                elif send_status == 1:
                    conn.sendall((RETRY_ERROR).to_bytes(1, byteorder='big') + pack_msg("Receiver Username Does Not Exist"))

            # List Accounts
            elif opcode == LIST:
                # Find accounts to be listed
                if len(args) == 0:
                    accounts = self.list_accounts("*")
                else:
                    search = args[0]
                    accounts = self.list_accounts(search)

                accounts_string = ""
                for account in accounts:
                    accounts_string += (account + "\n")

                conn.sendall((SUCCESS).to_bytes(1, byteorder='big') + pack_msg(accounts_string))

            # Log Out
            elif opcode == LOGOUT:
                # log out and break connection
                self.users[username].socket = None
                conn.sendall((SUCCESS).to_bytes(1, byteorder='big') + pack_msg("Logout Acknowledged!"))
                break

            # Delete
            elif opcode == DELETE:
                # delete account and break connection
                username = args[0]
                self.delete_account(username)
                conn.sendall((SUCCESS).to_bytes(1, byteorder='big') + pack_msg("Deleted Account!"))
                break

        # If we break out of the loop, we close the connection before return from this function
        conn.close()

    """ Function that handles connection """
    def handle_connection(self, conn):
        data = conn.recv(1024)
        server_or_client = data[0]

        if server_or_client == SERVER:
            port = int.from_bytes(data[1:5], 'big')
            self.handle_server_connection(conn, port)
        elif server_or_client == CLIENT:
            self.handle_client_connection(conn)
            print ("connected to client")

    """ Function to connect to other servers """
    def connect_to_servers(self):
        connection_message = (SERVER).to_bytes(1, byteorder = 'big') + (self.port).to_bytes(4, byteorder = 'big')
        for port in self.other_servers:
            self.other_servers[port].connect((self.host, port))
            self.other_servers[port].sendall(connection_message)

    """ Function to send a ping to other servers """
    def send_ping(self):
        update = (ALIVE).to_bytes(1, byteorder = 'big')

        # Current server is leader
        if self.id == self.master_id:
            update += (LEADER).to_bytes(1, byteorder = 'big') + (self.port).to_bytes(4, byteorder = 'big')
            for port in self.other_servers:
                self.other_servers[port].sendall(update)
                print("Sent ping from " + str(self.port) + " to " + str(port))

        # Current server is follower
        else:
            update += (FOLLOWER).to_bytes(1, byteorder = 'big') + (self.port).to_bytes(4, byteorder = 'big')
            for port in self.other_servers:
                self.other_servers[port].sendall(update)
                print("Sent ping from " + str(self.port) + " to " + str(port))

    """ Function that runs the server """
    def run(self):
        self.server.bind((self.host, self.port))
        self.server.listen()
        self.connect_to_servers()

        self.timer = RepeatedTimer(PING_INTERVAL, self.send_ping)

        while True:
            if self.id == self.master_id:
                conn, addr = self.server.accept()
                start_new_thread(self.handle_connection, (conn,))
            else:
                # Use the pairwise server connections made in init to ping the master every once in a while, and if it fails potentially become the master
                pass


def unit_tests():
    server = Server(0)
    # Test: Successfully creates account
    server.create_account("yejoo", "0104")
    assert(server.users["yejoo"].username == "yejoo")
    assert(server.users["yejoo"].password == "0104")

    # Test: Username must be unique
    server.create_account("yejoo", "0123")
    assert(server.users["yejoo"].username == "yejoo")
    assert(server.users["yejoo"].password == "0104")

    # Test: Listing Accounts
    server.create_account("idk", "sth")
    server.create_account("yej", "password")
    server.create_account("middle", "mid")
    assert(set(server.list_accounts("*")) == set(["yejoo", "yej", "idk", "middle"]))
    assert(set(server.list_accounts("ye*")) == set(["yejoo", "yej"]))
    assert(set(server.list_accounts("*oo")) == set(["yejoo"]))
    assert(set(server.list_accounts("*d*")) == set(["idk", "middle"]))

    # Test: Login only logs in users with correct passwords
    assert(server.login("yejoo", "0123") == 1)
    assert(server.login("yejoo", "0104") == 0)
    assert(server.login("idk", "sth") == 0)
    assert(server.login("dklfjsk;", "sdl k") == 2)
    assert(server.login("middle", "idk") == 1)

    # Test: sending message queues message
    server.send_message("yejoo", "idk", "secrete")
    server.send_message("yejoo", "idk", "dfjopadd")
    server.send_message("idk", "yejoo", "dofjsoi")
    sent_messages_idk = server.users["idk"].messages
    assert(len(sent_messages_idk) == 2)
    assert(sent_messages_idk[0].sender == "yejoo")
    assert(sent_messages_idk[0].receiver == "idk")
    assert(sent_messages_idk[0].message == "secrete")
    assert(sent_messages_idk[1].sender == "yejoo")
    assert(sent_messages_idk[1].receiver == "idk")
    assert(sent_messages_idk[1].message == "dfjopadd")
    sent_messages_yejoo = server.users["yejoo"].messages
    assert(len(sent_messages_yejoo) == 1)
    assert(sent_messages_yejoo[0].sender == "idk")
    assert(sent_messages_yejoo[0].receiver == "yejoo")
    assert(sent_messages_yejoo[0].message == "dofjsoi")

    # Test: receiving message looks at queued message
    assert(server.receive_messages("yejoo") == "From idk: dofjsoi\n")
    assert(server.receive_messages("idk") == "From yejoo: secrete\nFrom yejoo: dfjopadd\n")

    # Test: messages are received just once.
    assert(server.receive_messages("yejoo") == "")
    assert(server.receive_messages("idk") == "")

    # Test: deleted account returns messages and gets rid of user
    server.send_message("yejoo", "idk", "more")
    server.send_message("yejoo", "idk", "more2")
    server.delete_account("idk")
    assert("idk" not in server.users)
    assert(server.receive_messages("yejoo") == "")

def main():
    if len(sys.argv) != 2:
        print("Must provide the server id argument or unit test argument")
        return

    if sys.argv[1] == "test":
        unit_tests()
        print("Passes all unit tests")
        return

    id = int(sys.argv[1])
    if id not in [0, 1, 2]:
        print("Must provide a valid server id: 0, 1, 2")
        return

    server = Server(id)
    server.run()

main()
