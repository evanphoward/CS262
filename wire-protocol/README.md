# CS262-wire-protocol
Design Project 1: Wire Protocol, CS 262 Spring 2023
This is a messenger application with a Python backend. It has two separate implementations: one implementation where we have defined our own wire protocol and another implementation where we use gRPC.

# Setup
1. The only required library is gRPC for the gRPC version, which you can install via pip or conda if you don't have it installed. The wire protocol version should work out of the box.
2. Find your local IP Address and replace the HOST variable with that address in `client.py` and `server.py` (for wire protocol) and `grpc/chat_client.py` and `grpc/chat_server.py` (for gRPC).
    * For Mac, you can find this value by running `ifconfig ev0` in the terminal and copying the value after `inet`
    * For Windows, you can find this value by running `ipconfig` in the command prompt and copying the value after `IPv4 Address`

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
