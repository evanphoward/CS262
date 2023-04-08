import os
import socket
import pandas as pd

# Host IP for Server ID 1, 2, 3
HOSTS = ["127.0.0.1", "127.0.0.1", "127.0.0.1"]
# Port used is PORT + ID
PORT = 65432

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
            self.accounts = pd.read_csv(self.account_path)
        else:
            self.accounts = pd.DataFrame(columns = ["Username", "Password", "Time"])
            self.accounts.to_csv(self.account_path, index = False)

        if os.path.isfile(self.message_path):
            self.messages = pd.read_csv(self.message_path)
        else:
            self.messages = pd.DataFrame(columns = ["Sender", "Receiver", "Message", "Time"])
            self.messages.to_csv(self.message_path, index = False)

    """ Function to create a new account """
    # TODO: make sure that self.accounts is fresh before calling create_account
    def create_account(self, username, password):
        # Fails if username is not unique
        if username in self.accounts["Username"].values:
            return 1

        # Appends account to list of users otherwise and updates CSV file
        self.accounts.loc[len(self.accounts)] = [username, password, pd.Timestamp.now()]
        self.accounts.to_csv(self.account_path, index = False)
        return 0

    """ Function to log in """
    def login(self, username, password):
        match_username = self.accounts.loc[self.accounts["Username"] == username]

        # No matching username found. Fail.
        if len(match_username) == 0:
            return 2

        # Login if password matches. Fail otherwise
        if match_username["Password"][0] == password:
            return 0
        else:
            return 1

    """ Function to search and list all accounts """
    def list_accounts(search):
        accounts = ""
        # Find all matching usernames
        for username in self.accounts["Username"]:
            if fnmatch.fnmatch(username, search):
                accounts += username
                accounts += "\n"

        return accounts

    """ Function to send a message from one user to another """
    def send_message(sender, receiver, message):
        # Find receiver and queue message
        if receiver in self.accounts['Username'].values:
            # TODO: Figure out how we are delivering to the user, what the difference is when the user is logged in and isn't logged in
            return 0

        # Could not find receiver. Fail.
        return 1

    """ Function to receive all messages on behalf of user """
    def receive_messages(receiver):
        # Deliver all unread messages
        # TODO: Pending how we implement pending messages. Is the CSV cleared of all messages that match this receiver after we delvier them?

    """ Function to delete account """
    def delete_account(username):
        # Delete Account
        # TODO: Delete account from dataframe and from CSV file

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
    server.login("yejoo", "idk")

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
