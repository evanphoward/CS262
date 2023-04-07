# 04/07
To make replication easier, choosing to implement a Server class in [server.py] so that we can have multiple servers running (and implementing a consensus algorithm among servers later) if need be.
Within the Server class, to guarantee that messages & accounts don't get lost, persisting accounts / message database with a CSV file.
