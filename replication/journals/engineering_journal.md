# 4/7
To make replication easier, choosing to implement a Server class in [server.py] so that we can have multiple servers running (and implementing a consensus algorithm among servers later) if need be.
Within the Server class, to guarantee that messages & accounts don't get lost, persisting accounts / message database with a CSV file.

Copied over a few other server methods. Started to think about how the replication will work. I'm imagining we will have three concurrent servers (to maintain two fault tolerance). One server (initially ID 0) will be the primary. The primary will send state updates to the backup servers and the backup servers will continually ping the primary server. If a ping fails, then the primary will deterministcally become the server with the next ID (0 -> 1, 1 -> 2, 2 -> 0). Need to think about two servers failing but will address that later. Client would probably need to handle re-establishing a connection with the backup servers if this happens, not sure how we would get around that.

# 4/8
Choosing to make CSV queue all messages (and have a separate function later for receiving instantly if logged in). Then on delivery, CSV will delete messages from queue.
In addition to the two dataframes (accounts and messages), the server will also keep a dictionary of clients for ease of access & testing. The dictionary, unlike the dataframes, do not persist upon failure.
Python's hash function only guarantees same hash in a single session, so using backups and having to run a program multiple times means hash function for password is not consistent. Removing hash for now. Can deal with it later (but also doesn't seem to be the core of the design exercise).
Current unit tests only test for the server's version of events (i.e. self.users) and not actual persistence. Not sure if we should also try and test for persistence. (We probably should but seems like it would be quite tedious to do, so perhaps the assumption we should have is that the two are always aligned, which isn't too bad of an assumption)
Writing a general [handle_connection] function which will run on the server upon connection, distinguish whether it is a connection from another server or a client, and proceed accordingly. This also does mean client side should first connect with a ping and then do other stuff.
In terms of server-to-server connection, we probably want some ping to go between the servers to indicate that they have not failed and then regularly updating the replicas. Currently a ping sends information about 1. whether it is alive 2. whether it is a leader 3. port number. Maybe there are more things to be added there. Then, each server will have a thread that sends pings every second or something.

# 4/9
Modified client to deal with the fact that on connection it must send a messsage indicating it's a client

Added more complete client functionality, mostly copied from wire protocol implementation. All wire protocol functionality added to replication version with infrastructure to support replication, now to actually implement fail-over. Right now, when a server is killed other running servers continue running but display a BrokenPipeError.

Successfully got a very basic form of replication implemented -- if a server fails while no users are logged in, the next time they are logged in they will seamlessly be moved to a different server. All messages and accounts are persisted to the new server, using the same persistence infrastructure along with the primary server sending that information during a heartbeat ping. Next I'll work on that same sort of replication while a user is logged in.

Implemented failover while a user is logged in without too much difficulty. Uses the same method for connecting to a new server, but now keeps track of a logged in user and logs into the new server if a request to the old server ever fails.

Servers can now also come back online and be reconnected to by any existing servers. This means that as long as one server is still up, servers can come on and offline and the client's experience will be seamless.

# 4/10
Did some testing. Found some errors.
1. run server.py 0, server.py 1, then server.py 2. Then, kill server.py 0 and server.py 1. Restarting server.py 0 won't raise an issue but restarting server.py 1 will throw an error (it will think the connection is with a client).
2. run server.py 0, server.py 1, then server.py 2. Then, kill server.py 0 and server.py 1. Run client.py. Then, client does this on server 2. Restart server.py 0 and kill server.py 2. Then, the next command by the client will throw an error.

Confirmed Functionality:
- seamless client experience. (client connects to one server, said server goes down, client still sends requests and is received by another server)
- persistence. if all servers are brought down, account info & message info is not lost.
- 2-fault tolerance: If server0 goes down after having received a message, server1 still has sent message. If server1 goes down after having received a message, server2 still has sent message. If server2 goes down after having received a message, server0 still has sent message.
-
