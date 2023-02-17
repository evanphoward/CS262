# 2/8/23
Copied client / server stub files from TCP/IP intro tutorials online (https://realpython.com/python-sockets/ and https://www.geeksforgeeks.org/socket-programming-cc/).
One-to-one message passing out of the box for both the python-python communication and python-C++ communication on the same computer.
Used public ip address and localhost to try and host server and both failed. Found local IP address using "ifconfig ev0" and successfully established connection with Ye Joo's computer.
Talked about how to write a wire protocol, options like sending things as a string, constructing JSON as a string, arranging the bits and marshaling the data according to a wire protocol we write.

# 2/13/23
Spent a fair bit of time thinking about and testing setting up a Flask webapp and a Tkinter local app, but I think I will stick to command line i/o since it doesn't require any package installation or python version requirements. For Flask, the complexity was growing quicker than I would have liked and felt like I was allocating time and energy to something irrelevant to the assignment. For Tkinter there were fundamental issues with python versioning and most likely would have required debugging on the user's device. Unless I get a great idea for a GUI from someone else in the class or somewhere online, I'll stick with the command line.

# 2/17/23
Wrote some code for the client using a command line interface. Trying to abstract out all the functions for logging in, registering, connecting to a socket, and sending a request. Spent some time thinking about how to do the wire protocol -- I'd lean towards somehow packaging raw bytes, maybe using a byte array? Moved the server main code to a test function and added a TODO for the main server function.