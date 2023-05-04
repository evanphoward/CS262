import socket
from itertools import cycle
import select
import sys

HOST = "127.0.0.1"
PORT = 65432

SERVERS = [("127.0.0.1", 65433), ("127.0.0.1", 65434), ("127.0.0.1", 65435), ("127.0.0.1", 65436), ("127.0.0.1", 65437)]

# Algorithm Codes
ROUND_ROBIN = 0
LEAST_CONNECTIONS = 1

class LoadBalancer():
    """ Initialize LoadBalancer Object """
    def __init__(self, host = HOST, port = PORT, algorithm = LEAST_CONNECTIONS):
        self.host = host
        self.port = port
        self.algorithm = algorithm
        self.connections = {}
        self.num_connections = {server: 0 for server in SERVERS}

        # Create Client Socket
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.bind((self.host, self.port))
        self.client_socket.listen()
        self.sockets = [self.client_socket]
        if self.algorithm == ROUND_ROBIN:
            self.iterator = cycle(SERVERS)

    """ Function that handles selecting the server to load balance to """
    def select_server(self):
        if self.algorithm == ROUND_ROBIN:
            return next(self.iterator)
        elif self.algorithm == LEAST_CONNECTIONS:
            return min(self.num_connections, key=self.num_connections.get)

    """ Function that handles connection to load balancer """
    def handle_connection(self):
        conn, addr = self.client_socket.accept()
        self.sockets.append(conn)

        server_host, server_port = self.select_server()
        self.num_connections[(server_host, server_port)] += 1

        # Create Server Socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.connect((server_host, server_port))
        self.sockets.append(server_socket)

        # Add Connection Direction
        self.connections[conn] = server_socket
        self.connections[server_socket] = conn
        print(f"Connected client {conn.getpeername()} to server {server_socket.getpeername()}")

    """ Function that handles receiving data from appropriate socket """
    def handle_data(self, sock, data):
        # Find which socket to forward data to
        forward_to = self.connections[sock]
        forward_to.sendall(data)

        return

    """ Function that handles closed connection """
    def close_connection(self, sock):
        server_socket = self.connections[sock]
        self.num_connections[server_socket.getpeername()] -= 1

        # Close client-side socket and server-side socket
        sock.close()
        server_socket.close()

        # Remove client-side socket and server-side socket
        self.sockets.remove(sock)
        self.sockets.remove(server_socket)
        del self.connections[sock]
        del self.connections[server_socket]

        return

    """ Function that starts running the load balancer """
    def run(self):
        while True:
            try:
                sockets, _, _ = select.select(self.sockets, [], [])
            except ValueError:
                print("Too Many Sockets Open, trying again")
                continue
            # Iterate through all sockets
            for sock in sockets:
                # New Client Connction
                if sock == self.client_socket:
                    self.handle_connection()
                    break
                # Message from Existing Client Connection
                else:
                    data = sock.recv(1024)
                    if data:
                        self.handle_data(sock, data)
                    else:
                        self.close_connection(sock)
                        break

if __name__ == "__main__":
    if len (sys.argv) != 2:
        print ("How to Use: python3 load_balancer.py [algorithm].\nAvailable algorithms: round-robin, least-connections.")
        exit()

    algorithm = sys.argv[1]
    if algorithm == "round-robin":
        algo_code = ROUND_ROBIN
    elif algorithm == "least-connections":
        algo_code = LEAST_CONNECTIONS
    else:
        print ("How to Use: python3 load_balancer.py [algorithm].\nAvailable algorithms: round-robin, least-connections.")
        exit()

    loadbalancer = LoadBalancer(algorithm = algo_code)
    loadbalancer.run()

