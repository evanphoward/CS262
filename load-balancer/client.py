import socket

HOST = "127.0.0.1"
PORT = 65432

""" Class the represents a Client """
class Client():
    """ Initialize Client Object"""
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((HOST, PORT))

if __name__ == "__main__":
    client = Client()
