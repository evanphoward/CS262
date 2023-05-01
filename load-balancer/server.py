import socket
import sys
from _thread import *
import threading
import time
import numpy as np

RESPONSE_MEAN = 0.5
RESPONSE_VAR = 0.2
MAX_CONNECTIONS = 10

""" Class that represents a Server """
class Server():
    """ Initialize Server Object """
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.active_connections = 0
        self.connection_condition = threading.Condition()

    """ Handles Connction with Client """
    def handle_connection(self, conn):
        print(f"Connected to client {conn.getpeername()}")
        while True:
            data = conn.recv(1024)
            if not data:
                print(f"Closing connection to client {conn.getpeername()}")
                with self.connection_condition:
                    self.active_connections -= 1
                    self.connection_condition.notify()
                conn.close()
                break

            response_time = np.random.normal(RESPONSE_MEAN, RESPONSE_VAR)
            # Ensure response_time is non-negative, despite there being a very small probability
            while response_time < 0:
                response_time = np.random.normal(RESPONSE_MEAN, RESPONSE_VAR)
            time.sleep(response_time)
            conn.sendall(b"PONG!")

    """ Runs the server by listening to connections """
    def run(self):
        self.server.bind((self.host, self.port))
        self.server.listen()

        while True:
            conn, addr = self.server.accept()
            with self.connection_condition:
                while self.active_connections >= MAX_CONNECTIONS:
                    print("Maximum connections reached, waiting for available slot")
                    self.connection_condition.wait()
                self.active_connections += 1
                start_new_thread(self.handle_connection, (conn,))

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print ("How to Use: python3 server.py [host] [port]")
        exit()

    # Start server on host & port given by command line
    host = sys.argv[1]
    port = int(sys.argv[2])

    server = Server(host, port)
    server.run()
