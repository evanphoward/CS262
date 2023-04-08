import os
import socket
import pandas as pd
import sys
import fnmatch

# Host IP for Server ID 1, 2, 3
HOSTS = ["127.0.0.1", "127.0.0.1", "127.0.0.1"]
# Port used is PORT + ID
PORT = 65432

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

""" Class that represents a Server """
class Server():
    """ Initialize Server Object """
    def __init__(self, id):
        # Initialize host and port
        self.id = id
        self.master_id = 0
        self.host = HOSTS[id]
        self.port = PORT + id

        # TODO: Create pairwise socket connections a la logical clocks design problem

        # Create socket
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

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

    def run(self):
        self.server.bind((self.host, self.port))
        self.server.listen()

        while True:
            if self.id == self.master_id:
                conn, addr = self.server.accept()
                start_new_thread(handle_connection, (conn,))
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
    if id not in [1, 2, 3]:
        print("Must provide a valid server id: 1, 2, 3")
        return

    server = Server(id)
    server.run()

main()
