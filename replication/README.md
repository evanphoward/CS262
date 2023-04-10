# CS262-replication
Design Project 2: Replication, CS262 Spring 2023\
This is a chat application with that is persistent (it can be stopped and restarted without losing messages) and 2-fault tolerant.

# How to Use
You can start the three servers by running the following commands:
```console
python3 server.py 0
python3 server.py 1
python3 server.py 2
```
If you would like the replicated servers to run on different machines, different machines should run a different line of code.

You can start the client by running the following command:
```console
python3 client.py
```

# How to Test
In order to run unit tests that test server functionality, run the following command:
```console
python3 server.py test
```

# Functionality
- functionalities of a chat application: create account, list accounts, send message, deliver message, delete account
- persistence: the server can be stopped and restarted without losing accounts or messages
- 2-fault tolerance: failures can happen on up to 2 servers and the application can still continue to run

# Engineering Journal
The engineering journal can be found in replication/journals.
