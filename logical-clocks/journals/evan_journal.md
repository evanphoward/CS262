# 3/2/23
Thought about how to implement the three different processes and inter-process communication. Decided to have the three processes as three seperate python processes and have them communicate through sockets. At this point it seems like feeding the port to listen on as an argument is the most straight-forward solution. While there is probably a more elegant solution to getting the ports automaticaly, it doesn't seem worth the effort. 

Wrote some code to run a tick() function X times a second where X is the randomly chosen clock speed, instead of using a sleep() statement we use a while True loop that sees if a certain amount of time has passed so we don't run into an issue where tick() takes too long (unlikely but sendall may take a non-negligible amount of time, possibly).

Process spins up two threads to listen for messages from the other two processes and write them to a global message queue, which the tick() message checks when it runs for new messages. Need to use a lock for adding to that queue.

# 3/6/23
Debugged a weird bug I got while running trials where a process would get duplicate messages. Implemented a message end character so I could know where one ended and the next began as I thought that it had to do with receiving two messages at the same time. I found out the bug was in fact that both sockets in the sockets array were set to the same socket, so each process was only communicating with one other process. I removed the end character and started each process with a small delay so theorectically you could never have two processes send a message to the third at the same time.

Ran five trials at 90 seconds each, saved the log files as text files with more descriptive text and csv files for later analysis.

# 3/7/23
Continuing from Ye Joo's analysis. The first five runs are with the default settings prescribed by the specs. 

When the clock speeds don't differ enough that a single machine is stuck processing messages and falls behind, we can see that the clock of the fastest machine is always rising at a constant rate (since it is always the highest value), and the slower clocks drift away from that machine until they receive a message, at which point they jump back up to meet that machine's clock value.

Run-6 changes the possible clock speeds to be from 1 to 40, and we can see that machine 3 was much slower and the trend of it falling behind in clock and in messages remaining is even more apparent.

I was curious about three completely different clock speeds, and so for run-7 we have machine 1 with a clock speed of 1, 2 with a clock speed of 10, and 3 with a clock speed of 100. We can see that the drifting works and is a variable amount depending on how far the machines are from the fastest machine. Both machines 1 and 2 get stuck processing messages from machine 3, but since machine 2 is faster than machine 1 it doesn't fall behind as much.

For runs 8, 9, and 10, I did as suggested in the spec and changed the clock speed to only be 3 through 6, and made the chance of an internal event only 1/4 instead of 6/10. Overall, the results seemed largely similar to the standard runs. While the number of messages passed between processes went up quite a bit, they generally were able to keep up with each other since there was a smaller variation in the clock speed. In Run 8, which had a clock speed of 3 for machines 1 and 2 and 5 for machine 3, we can see that Machine 2 does build up quite a backlog, but is able to work it back down, corresponding with a drift away from machine 3's clock and then return to it.