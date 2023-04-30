 # 04/25
 Fixed the round robin logic so it would cycle through the servers. Added logging in the load balancer so you could see when a connection took place. Made the client ping the server and the server return a pong.

 # 04/29
The client now has a send_request method that measures and returns the response time in addition to the response data.

The load balancer has been updated to include five servers and the Least Connections algorithm has been implemented as an option for load balancing. (keep track of how many connections are at each server, select the one with the least connections)

The server now simulates a variable response time for each request, using a normal distribution with specified mean and variance. This was my effort to make things slightly more realistic but still able to see a difference between different algorithms.

`stress_test.py` spins up a specified number of parallel clients who then continually ping the load balancer a random number of times up to a max argument. It then outputs the response times for all the requests for each client to a json.

`generate_graphs.py` either generates a plot of the response times for the three jsons in `data/` (baseline one server, round robin w/ 5 servers, least connections w/ 5 servers) or generates more detailed graphs for an individual file

Doesn't seem to be a huge difference between the options. Probably want to run more trials or think about how to change various things (how we're connecting to the server, how parallel the servers can be) to have a more pronounced difference between the algorithms. Need to make slides!

# 04/30
Added `MAX_CONNECTIONS` to the server to simulate an overloaded server. Uses a threading condition to block a client until a server has less than `MAX_CONNECTIONS`.

Changed various aspects of `generate_graphs.py` to get more useful visualizations -- put the data and figures in their corresponding folders

Made a presentation