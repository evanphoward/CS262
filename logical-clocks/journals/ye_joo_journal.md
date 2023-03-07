# 2023.03.02
Thought about how to use sockets to connect each of the machines during initialization. There are probably more elegant solutions, but currently going with the approach where we basically assume that machine 1 starts first, machine 2 starts next, and then machine 3 starts. This way, there are no weird issues in terms of properly setting up the connection

# 2023.03.07.
Did some refactoring of code and added unit tests.
