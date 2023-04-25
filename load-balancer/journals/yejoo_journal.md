# 04/24
-Implemented load balancer big picture. Basically, load-balancer has client-side sockets and server-side sockets. The client-side socket waits for clients to connect to the load balancer. Then, upon connection, a server-side socket is created and used to connect the client to a selected server. The load balancer keeps track of which client and servers are connected by using a simple dictionary.
-The selection of the server above can be done using different algorithms. Currently just implemented the most simple "round robin" algorithm but it would be more interesting to do other stuff.
-Implemented basic client and server but they both don't do anything of substance or interest at the moment.

TODO:
1. do some more logging on load-balancer so it's clear when connections happen to client / to server
2. implement some sort of server/client functionality so that it's easier to determine if the code is working
3. think about different load balancing algorithms
