# CS262-wire-protocol
Design Project 1: Wire Protocol, CS 262 Spring 2023
This is a messenger application with a Python backend. It has two separate implementations: one implementation where we have defined our own wire protocol and another implementation where we use gRPC.

# Setup
TODO: do they need to install anything?
TODO: do they need to modify code to specify the host/port? (and should we explain this?)

# How to Use
## Wire Protocol Version
You can start the server by running the following code in the directory:
```console
python3 server.py
```
You can start the client by running the following code in the directory:
```console
python3 client.py
```

## gRPC Version
In order to use the gRPC version, first enter the `grpc` directory by running the following:
```console
cd grpc
```

You can start the server by running the following code:
```console
python3 chat_server.py
```
You can start the client by running the following code:
```console
python3 chat_client.py
```

# Functionality
- create account
- list accounts
- send message
- deliver message
- delete account
