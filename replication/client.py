import socket

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 65432  # The port used by the server

# Connection Codes
SERVER = 0
CLIENT = 1

class Client():
    def __init__(self):
        return

    def run(self):
        # Create socket for connection and send connection message to server
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((HOST, PORT))
        connection_message = (CLIENT).to_bytes(1, byteorder = 'big')
        s.sendall(connection_message)

def main():
    client = Client()
    client.run()

main()
