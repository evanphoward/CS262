# Comparisons between gRPC and Wire Protocol
We wrote our non-gRPC version first and had all functionality complete before we wrote the gRPC version -- this certainly informed our design of the gRPC version, with it mostly following the same design but with gRPC calls rather than a wire protocol packet being sent over a socket. This design decision also meant that we went back and changed some things in our wire protocol version to make it map to the request / response paradigm that gRPC imposes. 

### Code Complexity
The code is certainly much simpler in the gRPC version, with no argument packing into the wire protocol and simple one line calls to the server in many cases. Because the gRPC channels aren't explicitly available like sockets are available there are a few more metadata things like the LOGGED_IN users or needing to send the username to logout or delete accounts, but those are relatively minor additions. Simply going by lines of code, you can see that the gRPC versions are much shorter, despite being relatively the same approach to implementation (not including the gRPC stubs, of course, which does boost the line count and increase complexity, although it is more invisible complexity to us).

### Packet Size
In the wire protocol version, our packets are generally just the arguments needed for a call plus a few extra bytes for metadata (arugment length, opcode). For the gRPC version, we send the same information through the protocol buffer, but because the protocol buffer has more metadata, the protocol buffers are going to be bigger than the custom-built very lightweight wire protocol that we wrote. 
(TODO: Get the exact numbers for each and compare them? Should be easy to get the length of the bytes we send in the wire protocol version, idk how to see size of protocol buffer in gRPC)

### Performance Comparison
TODO: Not sure exactly how to compare these two. Time the code?

# Engineering Journal
## 2/8
### Evan
Copied client / server stub files from TCP/IP intro tutorials online (https://realpython.com/python-sockets/ and https://www.geeksforgeeks.org/socket-programming-cc/).
One-to-one message passing out of the box for both the python-python communication and python-C++ communication on the same computer.
Used public ip address and localhost to try and host server and both failed. Found local IP address using "ifconfig en0" and successfully established connection with Ye Joo's computer.
Talked about how to write a wire protocol, options like sending things as a string, constructing JSON as a string, arranging the bits and marshaling the data according to a wire protocol we write.

### Ye Joo
Established connection between two computers on same network.
Python's sendall handles encoding & decoding in the process.
Should establish wire protocol for creating account / logging in / sending message / receiving message / deleting account.

https://realpython.com/python-sockets/
https://pythontic.com/modules/socket/send
https://stackoverflow.com/questions/21810776/str-encode-adds-a-b-to-the-front-of-data

## 2/13
### Evan
Spent a fair bit of time thinking about and testing setting up a Flask webapp and a Tkinter local app, but I think I will stick to command line i/o since it doesn't require any package installation or python version requirements. For Flask, the complexity was growing quicker than I would have liked and felt like I was allocating time and energy to something irrelevant to the assignment. For Tkinter there were fundamental issues with python versioning and most likely would have required debugging on the user's device. Unless I get a great idea for a GUI from someone else in the class or somewhere online, I'll stick with the command line.

## 2/16
### Ye Joo
create_account: supplies username and password (authentication) to ensure only user accesses account
Keeping a list of accounts for now, may start using SQL db at some point. (Same deal for messages)
create_account: currently returning -1 or 0 for failure/success --> should send a message to client rather.
Testing on main() for now, should do unit testing later.
list_accounts: Listing accounts should go through USERS and send them to client --> need protocol for this.
login: should alert client on failure (and type of failure - no id or password not matching)
login: should keep track of who we are logged in as, probably in main (to be implemented)
send_message: should decide between 1) always queueing message and delivering upon request from other user 2) delivering immediately. (2) seems more real world friendly but harder to implement.
receive_messages: should have wire protocol that probably delivers one message at a type. what happens when you fail in the middle?
delete_account & receive_messages: there's a failure case if username is not in USERS or MESSAGES that's not handled at the moment. might be unnecessary (based on how app is designed, we could just take the current user's username) but also makes the functions pretty failure-prone in their absence.
delete_account: returning undelivered messages to sender since that seems the most reasonable (and sender would want to know this!)
side note: make USERS a dict? constant access to username rather than traversing! --> actually gonna do that lol

## 2/17
### Evan
Wrote some code for the client using a command line interface. Trying to abstract out all the functions for logging in, registering, connecting to a socket, and sending a request. Spent some time thinking about how to do the wire protocol -- I'd lean towards somehow packaging raw bytes, maybe using a byte array? Moved the server main code to a test function and added a TODO for the main server function.

## 2/18
### Evan
Added a bunch of client functionality, actually making the requests to the server using a very basic wire protocol. The wire protocol is the opcode as the first byte, then the arguments for that opcode in order. Each argument's first byte is the length of the rest of the argument, and the rest is the actual argument which must be the length given. Implemented the start of the receiving code on the server and implemented a "PING" opcode that returns a "PONG!" message and this works. Added TODOs for some of the thoughts on next steps == we need to think about how received messages get communicated to a user, both when they first log in and while they are logged in. Ideally we want a push system but the user also needs to be able to make requests dynamically while also listening for the messages. Multi-threading in the client??? Probably don't need that but something that came to mind. Tried to implement various error checking as the ideas came to me -- for the wire protocol from the server to the client, the first byte is 0 if the response is successful and non-zero if there's an error. In the client code itself usually the functions return multiple values with the first value following that same error pattern. I've preliminarily made a 1 be a connection error that currently just closes the client, and 2 represents a user error or some other error that means the request should be retried (maybe with the proper arguments).

## 2/19
### Evan
In order to solve the problem of both listening for messages in the client and also waiting for user input, we've decided to make the client multithreaded -- with one thread listening for messages from the server and the other listening for user input from the user. We'll use a lock so that if the user is currently trying to perform an operation the lock is held, and if the client received a message from the server and is printing to the user the lock is also held.

### Ye Joo
implementing wire protocol on server side. some redundancy in parsing wire protocol arguments (ex: login and register have exact same arguments) --> try to clean up later.
Question for self: should handle_connection have different error codes for different errors that occur? (ex: incorrect password vs. username not found) It doesn't seem that useful at the moment.
for listing accounts & receiving messages, current pack_msg seems failure prone

## 2/20
### Evan
Thinking about how to send messages back to the user. When a user sends another user a message, if that user is logged in then the message should be delivered immedietely. Otherwise it should be delivered the next timat that user logs in. Some thoughts: 
1. Sockets could be stored somewhere global in the server and the sending thread could get the receiver's socket and send the messages along.
2. The receiver's thread could check for messages after handling a request from that user

Implemented number 1 and it seems to work reasonably well. This should handle the case where there are undelivered messages and they delete their account since it should be impossible to have undelivered messages while logged in, so i don't think we need to handle that case. I'm not sure if listing users is working since If I have user "evan" and I type "ev*" it doesn't list that account, need to debug that. Still need to reimplement everything in grpc

I've realized that the current approach of decoupling listening for input and listening for messages from the server is fundamentally incompatible with the gRPC approach. I've decided to rewrite the client in order to make it singlethreaded and handle these things in a more request/response way. Current problem is that our current wire protocol doesn't give us an easy way to handle more than one message in a single response i.e. the packets don't start in a consistent way.

Ohhhh, python gives you a bytes array that is the exact length of the response it received, the 1024 argument is just the max length. That makes it easier.

Reconfigured parse_response in the client to get every message sent from the server. In send_request, it prints all the messages it gets (First byte is 3), and then returns the singular response for the request that it sent. That means that currently a user only gets its messages when they log-in or when they make a request to the server which isn't ideal.

Thinking more about how gRPC operates, I've decided to simplify things further by requiring the user to actively check their messages in order to see the received messsages. Messages are still sent to the client as soon as they are received by the server, they just aren't displayed to the user until they ask for them, delete their account, or log out.

Started to implement gRPC based on tutorials at https://grpc.io/docs/languages/python/quickstart/ and https://grpc.io/docs/languages/python/basics/. As it stands, need to copy over code from our server.py and try to implement the various functions in the server class. Big questions for me are how we will be sending messages to the user (initial thought is to turn the check message button into a request to the server, where the server is storing the messages).

### Ye Joo
OS Error: Bad File Descriptor --> trying to resolve this error. Seems to be triggered by doing conn.close() in handle_connections (getting rid of it makes the error go away). Probably has something to do with trying to receive from an already closed connection.
Cleaned up parsing the request according to wire protocol.
Getting Indexing Error when parsing "list" request because when the user inputs blank but server expects one argument. Fixing on client side.
Adding wildcard matching in list_account functionality. Document for user.
Converted print tests to unit tests. I do wonder if receive_message should work the way it does right now (stacking up strings). An alternative way to do it is to just have a list and then packing arguments, which almost seems more reasonable. (This would require change in server --> client protocol)
Account Deletes --> queueing return message back to MESSAGES to be delievered like any other message, just with the information that the account has been deleted

## 2/21
### Evan
Implemented listing users and copied some boilerplate from non-grpc version to grpc client. Thinking now about how to implement message receiving. Ye joo suggested using response streaming, and after some research this is my current thinking: when a user logs in, they make a request for receiving messages, but then doesn't check the stream. Whenever a user checks their messages, they get all the messages waiting in the stream. Are grpc servers inherently multithreaded, allowing the server to wait in this function? I guess so since they don't have a single connection to a single user anyway.

First pass and message receiving seems to work! Streaming didn't work exactly as I thought -- basically the stream object is an python iterator but you block on iterating until you get the next object. So I spawned a new thread that added any received messages to a global object, which we could then treat the same way we treated the corresponding object in the non-grpc version

Fixed error Ye Joo found, it had to do with Login sending multiple responses when a user had messages waiting for them. Our wire protocl version has an invariant that each request must return exactly one response from the server, otherwise we may have bugs like that.

### Ye Joo
Debugged wildcard matching error (it had to do with wire protocol sending over first char of search term rather than entire string).
Debugged unbound local error for RECEIVED_MESSAGES due to local/global scoping issue.
Changed server side code to the actual delete implementation: once account is deleted, remaining messages get delivered to user before the user leaves.

Generally tested functions in non-grpc chat case. Just one error case.
The initial messaging seems to work but one thing I've tried that doesn't properly work (maybe it's just me):
if yejoo sends evan message, yejoo logs out, evan logs in, evan logs out, then upon log out evan will see message
if yejoo sends evan message, yejoo logs out, evan logs in, evan clicks check message, then there will be no message, when evan tries to log out it will pring PONG?

Started working on grpc server side. Distinction between unary and stream seem useful --> we probably want some of these to be streaming multiple responses rather than strings.
Implemented login and register to be unary.

Thoughts on grpc for tm morning:
1. Create a message-stream listener that will listen to messages from the server --> this could mean not having to deal with getting messages specifically at login?
2. Test making List a unary_stream
3. Maybe Delete/Receive should also get user info and then stream messages

Currently listed server functionalities except receiving messages implemented. Server can serve, but actual functionality not tested at all.
Started working on client side and am getting that grpc has no attribute 'Response', not sure why this is happening. Ok figured it out, it seems the grpc.py keeps track of the rpc info and the pb2.py keeps track of the things that go on rpcs so gotta use that instead.
Now getting Protocol message Response has no \"retType\" field." this error. Does not make much sense to me given chat.proto has this?
python -m grpc_tools.protoc -I. --python_out=. --pyi_out=. --grpc_python_out=. ./chat.proto 
Ran this command again and now that error is gone lol
Login/Register (without any additional functionalities) work now I think

Testing around a bit more.
non-grpc: I think the error case I found earlier is still happening! yejoo registers, evan registers, evan sends yejoo message, yejoo logs in, yejoo "checks" messages, no messages appear, upon logout yejoo gets a pong.
grpc: things seem to be working well!



