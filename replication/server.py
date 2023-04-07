import os
import socket
import pandas as pd

HOST = "127.0.0.1"
PORT = 65432

class Server():
    """ Initialize Server Object """
    def __init__(self, host_and_port = None):
        # Initialize host and port
        if host_and_port is None:
            self.host = HOST
            self.port = PORT
        else:
            self.host = host_and_port[0]
            self.port = host_and_port[1]

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

    def run(self):
        self.server.bind((self.host, self.port))
        self.server.listen()

        while True:
            conn, addr = self.server.accept()
            start_new_thread(handle_connection, (conn,))

def main():
    server = Server()
    server.login("yejoo", "idk")
    server.run()

main()
