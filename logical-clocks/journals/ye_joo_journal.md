# 2023.03.02
Thought about how to use sockets to connect each of the machines during initialization. There are probably more elegant solutions, but currently going with the approach where we basically assume that machine 1 starts first, machine 2 starts next, and then machine 3 starts. This way, there are no weird issues in terms of properly setting up the connection

# 2023.03.07.
Did some refactoring of code and added unit tests.
Visualized the 5 experimental runs by Evan (visualize.py).

# Analysis
run1: machine1 had 3 ticks per sec, machine2 had 3 ticks per sec, machine3 had 2 ticks per sec.
- machine 1 and machine 2 were more consistent in their logical clock, machine 3 had more variation.
- number of remaining messages to read from queue was never larger than 2. generally, machines were pretty well-synced with respect to each other.
run2: machine1 had 6 ticks per sec, machine2 had 4 ticks per sec, machine3 had 4 ticks per sec.
- machine 2 and machine 3 were drifting toward the logical clock values of machine 1
- number of remaining messages to read from queue was never larger than 1.
run3: machine1 had 1 tick per sec, machine2 had 5 ticks per sec, machine3 had 2 ticks per sec.
- machine 1 and machine 3 were both drifting toward machine 2's logical clock value. machine 3 remained fairly close to machine 2, but machine 1 did not catch up as quickly.
- machine 1 ended up piling up with lots of messages on the queue (15 at one point), which probably contributes to not being able to catch up with the logical clock. machine 3 occasionally had messages pile up, but it was nowhere near significant as machine1.
run4: machine1 had 5 ticks per sec, machine2 had 6 ticks per sec, machine3 had 3 ticks per sec.
- machine2 had the highest logical clock value usually and the other two machines would drift toward it, but the three logical clocks were aligned fairly well
- messages on machine3's queue occasionally piled up (up to 4), but machine1 or machine2 rarely had this issue.
run5: machine1 had 2 ticks per sec, machine2 had 6 ticks per sec, machine3 had 6 ticks per sec.
- machine 2 and machine 3 were pretty well aligned, with machine 1 dritfting to the larger logical clock values
- machine 1 had messages pile up in the queue quite a bit (up to 5), whereas machine 2 and machine 3 rarely had this issue.

# Takeaways
- generally, the machines drift to the largest logical clock value (machine with fastest clock cycle)
- if there isn't significant variation in the clock cycle, the machines tend to stay pretty consistent. however, if there is significant variation, the slower machines tend to fall behind.
- machines falling behind can also be seen as a result of messages piling up on the queue. machines can only open one message at a time, so the slower machines have a harder time catching up as more messages pile up on the queue.
