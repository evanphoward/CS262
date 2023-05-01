import socket
import time

HOST = "127.0.0.1"
PORT = 65432

""" Class the represents a Client """
class Client():
    """ Initialize Client Object"""
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((HOST, PORT))

    """ Function that sends request to server """
    def send_request(self, data):
        start_time = time.time()
        self.socket.sendall(data)
        response = self.socket.recv(1024)
        response_time = time.time() - start_time
        return response, response_time

if __name__ == "__main__":
    client = Client()
    response, response_time = client.send_request(b"PING!")
    print(response)
    print(f"Response time: {response_time:.4f} seconds")
