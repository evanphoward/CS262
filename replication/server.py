import os
import socket
import pandas as pd

HOST = "127.0.0.1"
PORT = 65432

class Server():
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

        # Create account dictionary and corresponding CSV file
        self.accounts = {}
        self.path = "server-" + str(self.port) + ".csv"
        if os.path.isfile(self.path):
            self.messages = pd.read_csv(self.path)
        else:
            self.messages = pd.DataFrame(columns = ["Sender", "Receiver", "Message", "Time"])
            self.messages.to_csv(self.path)

    def run(self):
        self.server.bind((self.host, self.port))
        self.server.listen()

        while True:
            conn, addr = self.server.accept()
            start_new_thread(handle_connection, (conn,))

def main():
    server = Server()
    server.run()

main()
