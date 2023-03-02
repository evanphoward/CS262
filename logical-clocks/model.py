import socket
from _thread import *
import threading
import time
import random

CLOCK = 0
MESSAGE_QUEUE = []
QUEUE_LOCK = threading.Lock()

SEND_TO_ONE = 1
SEND_TO_TWO = 2
SEND_TO_BOTH = 3

def get_socket(id):
    pass

def listen(s):
    global MESSAGE_QUEUE
    while True:
        msg = s.recv(1024)
        if not msg:
            return
        try:
            receiving_time = int(msg)
            QUEUE_LOCK.acquire()
            MESSAGE_QUEUE.append(receiving_time)
            QUEUE_LOCK.release()
        except ValueError:
            print("ValueError: Non-numeric message sent: " + msg)

def tick(s1, s2):
    global MESSAGE_QUEUE, CLOCK
    if MESSAGE_QUEUE:
        action = "Action: Received Message"
        msg = MESSAGE_QUEUE.pop(0)
        CLOCK = max(msg, CLOCK) + 1
    else:
        opcode = random.randint(1, 10)
        if opcode == SEND_TO_ONE:
            # TODO: Have some identification of s1 and s2 for logging
            action = "Action: Sent Message to "
            s1.sendall(str(CLOCK))
        elif opcode == SEND_TO_TWO:
            action = "Action: Sent Message to "
            s2.sendall(str(CLOCK))
        elif opcode == SEND_TO_BOTH:
            action = "Action: Sent Message to both processes"
            s1.sendall(str(CLOCK))
            s2.sendall(str(CLOCK))
        else:
            action = "Action: Internal Event"
        CLOCK += 1
    write_to_log(action + ", System Time: " + time.strftime('%H:%M:%S', time.time()) + ", Logical Clock" + CLOCK)

def write_to_log(log):
    pass

def main():
    clock_speed = random.randint(1, 6)

    # TODO: Figure out how to determine ID of this process (1,2,3) and set up socket
    s1 = get_socket(1)
    s2 = get_socket(2)
    start_new_thread(listen, (s1,))
    start_new_thread(listen, (s2,))

    start = time.time()
    period = 1.0 / clock_speed
    while True:
        if (time_time() - start) > period:
            start += period
            tick(s1, s2)

main()