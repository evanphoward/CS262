# CS262-replication
Design Project 2: Replication, CS262 Spring 2023\
This is a chat application that is persistent (it can be stopped and restarted without losing messages) and 2-fault tolerant.

# How to Use
You can start the three servers by running the following commands:
```console
python3 server.py 0
python3 server.py 1
python3 server.py 2
```
If you would like the replicated servers to run on different machines, you must modify the IP addresses in the global variable `HOSTS` in both `client.py` and `server.py`, to match the IP addresses of the three servers.

You can start the client by running the following command:
```console
python3 client.py
```

This is fully distributed, with all servers and all clients being able to be run on different machines.

# How to Test
In order to run unit tests that test server functionality, run the following command:
```console
python3 server.py test
```

# Functionality
- functionalities of a chat application: create account, list accounts, send message, deliver message, delete account
- persistence: the server can be stopped and restarted without losing accounts or messages
- 2-fault tolerance: failures can happen on up to 2 servers and the application can still continue to run
- as long as one server remains online, other servers can go offline and back online and still remain functionality and persistent -- seamless experience from the client's perspective (e.g. If only server 3 is up, then server 1 comes back up, server 3 could then go down and clients could still communicate with server 1)

# Engineering Journal
The engineering journal can be found in replication/journals.
