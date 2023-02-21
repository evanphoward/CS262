# 2/8/23
Copied client / server stub files from TCP/IP intro tutorials online (https://realpython.com/python-sockets/ and https://www.geeksforgeeks.org/socket-programming-cc/).
One-to-one message passing out of the box for both the python-python communication and python-C++ communication on the same computer.
Used public ip address and localhost to try and host server and both failed. Found local IP address using "ifconfig ev0" and successfully established connection with Ye Joo's computer.
Talked about how to write a wire protocol, options like sending things as a string, constructing JSON as a string, arranging the bits and marshaling the data according to a wire protocol we write.

# 2/13/23
Spent a fair bit of time thinking about and testing setting up a Flask webapp and a Tkinter local app, but I think I will stick to command line i/o since it doesn't require any package installation or python version requirements. For Flask, the complexity was growing quicker than I would have liked and felt like I was allocating time and energy to something irrelevant to the assignment. For Tkinter there were fundamental issues with python versioning and most likely would have required debugging on the user's device. Unless I get a great idea for a GUI from someone else in the class or somewhere online, I'll stick with the command line.

# 2/17/23
Wrote some code for the client using a command line interface. Trying to abstract out all the functions for logging in, registering, connecting to a socket, and sending a request. Spent some time thinking about how to do the wire protocol -- I'd lean towards somehow packaging raw bytes, maybe using a byte array? Moved the server main code to a test function and added a TODO for the main server function.

# 2/18/23
Added a bunch of client functionality, actually making the requests to the server using a very basic wire protocol. The wire protocol is the opcode as the first byte, then the arguments for that opcode in order. Each argument's first byte is the length of the rest of the argument, and the rest is the actual argument which must be the length given. Implemented the start of the receiving code on the server and implemented a "PING" opcode that returns a "PONG!" message and this works. Added TODOs for some of the thoughts on next steps == we need to think about how received messages get communicated to a user, both when they first log in and while they are logged in. Ideally we want a push system but the user also needs to be able to make requests dynamically while also listening for the messages. Multi-threading in the client??? Probably don't need that but something that came to mind. Tried to implement various error checking as the ideas came to me -- for the wire protocol from the server to the client, the first byte is 0 if the response is successful and non-zero if there's an error. In the client code itself usually the functions return multiple values with the first value following that same error pattern. I've preliminarily made a 1 be a connection error that currently just closes the client, and 2 represents a user error or some other error that means the request should be retried (maybe with the proper arguments).

# 2/19/23
In order to solve the problem of both listening for messages in the client and also waiting for user input, we've decided to make the client multithreaded -- with one thread listening for messages from the server and the other listening for user input from the user. We'll use a lock so that if the user is currently trying to perform an operation the lock is held, and if the client received a message from the server and is printing to the user the lock is also held.

# 2/20/23
Thinking about how to send messages back to the user. When a user sends another user a message, if that user is logged in then the message should be delivered immedietely. Otherwise it should be delivered the next timat that user logs in. Some thoughts: 
1. Sockets could be stored somewhere global in the server and the sending thread could get the receiver's socket and send the messages along.
2. The receiver's thread could check for messages after handling a request from that user

Implemented number 1 and it seems to work reasonably well. This should handle the case where there are undelivered messages and they delete their account since it should be impossible to have undelivered messages while logged in, so i don't think we need to handle that case. I'm not sure if listing users is working since If I have user "evan" and I type "ev*" it doesn't list that account, need to debug that. Still need to reimplement everything in grpc

I've realized that the current approach of decoupling listening for input and listening for messages from the server is fundamentally incompatible with the gRPC approach. I've decided to rewrite the client in order to make it singlethreaded and handle these things in a more request/response way. Current problem is that our current wire protocol doesn't give us an easy way to handle more than one message in a single response i.e. the packets don't start in a consistent way.

Ohhhh, python gives you a bytes array that is the exact length of the response it received, the 1024 argument is just the max length. That makes it easier.

Reconfigured parse_response in the client to get every message sent from the server. In send_request, it prints all the messages it gets (First byte is 3), and then returns the singular response for the request that it sent. That means that currently a user only gets its messages when they log-in or when they make a request to the server which isn't ideal.

Thinking more about how gRPC operates, I've decided to simplify things further by requiring the user to actively check their messages in order to see the received messsages. Messages are still sent to the client as soon as they are received by the server, they just aren't displayed to the user until they ask for them, delete their account, or log out.

Started to implement gRPC based on tutorials at https://grpc.io/docs/languages/python/quickstart/ and https://grpc.io/docs/languages/python/basics/. As it stands, need to copy over code from our server.py and try to implement the various functions in the server class. Big questions for me are how we will be sending messages to the user (initial thought is to turn the check message button into a request to the server, where the server is storing the messages).