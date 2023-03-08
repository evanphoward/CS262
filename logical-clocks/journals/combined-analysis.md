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

Evan's Analysis, continuing from Ye Joo's analysis. The first five runs are with the default settings prescribed by the specs. 

When the clock speeds don't differ enough that a single machine is stuck processing messages and falls behind, we can see that the clock of the fastest machine is always rising at a constant rate (since it is always the highest value), and the slower clocks drift away from that machine until they receive a message, at which point they jump back up to meet that machine's clock value.

Run-6 changes the possible clock speeds to be from 1 to 40, and we can see that machine 3 was much slower and the trend of it falling behind in clock and in messages remaining is even more apparent.

I was curious about three completely different clock speeds, and so for run-7 we have machine 1 with a clock speed of 1, 2 with a clock speed of 10, and 3 with a clock speed of 100. We can see that the drifting works and is a variable amount depending on how far the machines are from the fastest machine. Both machines 1 and 2 get stuck processing messages from machine 3, but since machine 2 is faster than machine 1 it doesn't fall behind as much.

For runs 8, 9, and 10, I did as suggested in the spec and changed the clock speed to only be 3 through 6, and made the chance of an internal event only 1/4 instead of 6/10. Overall, the results seemed largely similar to the standard runs. While the number of messages passed between processes went up quite a bit, they generally were able to keep up with each other since there was a smaller variation in the clock speed. In Run 8, which had a clock speed of 3 for machines 1 and 2 and 5 for machine 3, we can see that Machine 2 does build up quite a backlog, but is able to work it back down, corresponding with a drift away from machine 3's clock and then return to it.