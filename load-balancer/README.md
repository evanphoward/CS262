# CS262-Load-Balancer
Final Project: Load Balancer, CS262 Spring 2023\
This is a socket implementation of a load balancer that balances tasks that are requested from the client to the server.

# How to Use
You can start a server by running the following command:
``` console
python3 server.py [host] [port]
```
For the sake of seeing the load balancer actually at work, it is recommended that you start multiple servers.\
Additionally, the host and port numbers of servers are designated in `load_balancer.py` as variable `SERVERS`. In order to have servers on different machiens or different ports, this variable should be changed.

You can start the load balancer by running the following command:
``` console
python3 load_balancer.py [algorithm]
```
Currently, the available algorithms are `round-robin`, which iterates through all of the servers in order and `least-connections` which chooses the server that currently has the least connections.

Once the servers and the load balancer are running, you can start up a client that will connect to a load balancer and send a request to a server that is selected by the load balancer by running the following command:
```console
python3 client.py
```

# How to Test with Multiple Clients
Once the servers and load balancer are running, you can stress test the load balancer by running the following command:
```console
python3 stress_test.py [number_of_clients] [max_number_of_requests]
```

This will set up a number of concurrent clients that send requests to the load balancer. Additionally, it will create a `response_times.json` file that records the response time that it took for the load balancer to handle each client.

Once the load balancer generates data via stress-testing using different algorithms, you can rename each of them `data/Baseline.json`, `data/RoundRobin.json`, `data/LeastConnections.json` based on the algorithm that was used in the load balancer. Then, you can run the following command in order to generate a result graph:
```console
python3 generate_graphs.py
```

# Functionality
- server: Server receives ping requests from client and responds
- client: Client sends ping requests to server
- load balancer: load balancer maintains connections to servers and to clients and upon client connection chooses a server that the client connects to
- stress tester: stress tester starts up multiple clients concurrently and sends multiple requests to the load balancer in order to measure response time

# Engineering Journal
The engineering journal can be found in load-balancer/journals.

