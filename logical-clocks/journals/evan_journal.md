# 3/2/23
Thought about how to implement the three different processes and inter-process communication. Decided to have the three processes as three seperate python processes and have them communicate through sockets. At this point it seems like feeding the port to listen on as an argument is the most straight-forward solution. While there is probably a more elegant solution to getting the ports automaticaly, it doesn't seem worth the effort. 

Wrote some code to run a tick() function X times a second where X is the randomly chosen clock speed, instead of using a sleep() statement we use a while True loop that sees if a certain amount of time has passed so we don't run into an issue where tick() takes too long (unlikely but sendall may take a non-negligible amount of time, possibly).

Process spins up two threads to listen for messages from the other two processes and write them to a global message queue, which the tick() message checks when it runs for new messages. Need to use a lock for adding to that queue.

# 3/6/23
Debugged a weird bug I got while running trials where a process would get duplicate messages. Implemented a message end character so I could know where one ended and the next began as I thought that it had to do with receiving two messages at the same time. I found out the bug was in fact that both sockets in the sockets array were set to the same socket, so each process was only communicating with one other process. I removed the end character and started each process with a small delay so theorectically you could never have two processes send a message to the third at the same time.

Ran five trials at 90 seconds each, saved the log files as text files with more descriptive text and csv files for later analysis.