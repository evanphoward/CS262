# 04/07
To make replication easier, choosing to implement a Server class in [server.py] so that we can have multiple servers running (and implementing a consensus algorithm among servers later) if need be.
Within the Server class, to guarantee that messages & accounts don't get lost, persisting accounts / message database with a CSV file.

# 04/08
Choosing to make CSV queue all messages (and have a separate function later for receiving instantly if logged in). Then on delivery, CSV will delete messages from queue.
In addition to the two dataframes (accounts and messages), the server will also keep a dictionary of clients for ease of access & testing. The dictionary, unlike the dataframes, do not persist upon failure.
Python's hash function only guarantees same hash in a single session, so using backups and having to run a program multiple times means hash function for password is not consistent. Removing hash for now. Can deal with it later (but also doesn't seem to be the core of the design exercise).
Current unit tests only test for the server's version of events (i.e. self.users) and not actual persistence. Not sure if we should also try and test for persistence. (We probably should but seems like it would be quite tedious to do, so perhaps the assumption we should have is that the two are always aligned, which isn't too bad of an assumption)
Writing a general [handle_connection] function which will run on the server upon connection, distinguish whether it is a connection from another server or a client, and proceed accordingly. This also does mean client side should first connect with a ping and then do other stuff.
In terms of server-to-server connection, we probably want some ping to go between the servers to indicate that they have not failed and then regularly updating the replicas. Currently a ping sends information about 1. whether it is alive 2. whether it is a leader 3. port number. Maybe there are more things to be added there. Then, each server will have a thread that sends pings every second or something.

# 04/09
Modified client to deal with the fact that on connection it must send a messsage indicating it's a client
