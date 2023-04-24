import socket

HOST = "127.0.0.1"
PORT = 65432

# Algorithm Codes
ROUND_ROBIN = 0

class LoadBalancer():
    """ Initialize LoadBalancer Object """
    def __init__(self, host = HOST, port = PORT, algorithm = ROUND_ROBIN):
        self.host = host
        self.port = port
        self.algorithm = algorithm

        # Create Socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.host, self.port))
        sock.listen()
        self.sockets = [sock]

    """ Function that handles selecting the server to load balance to """
    def select_server(self):
        pass

    """ Function that handles connection to load balancer """
    def handle_connection(self):
        pass

    """ Function that handles closed connection """
    def close_connection(self):
        pass

    """ Function that starts running the load balancer """
    def run(self):
        pass

if __name__ == "__main__":
    loadbalancer = LoadBalancer()
    loadbalancer.run()

