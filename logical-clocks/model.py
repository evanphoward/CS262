import time, random

MESSAGE_QUEUE = []

def get_socket(id):
    pass

def listen(s):
    while True:
        msg = s.recv(1024)
        if not msg:
            return
        MESSAGE_QUEUE.append(msg)

def tick():

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
            tick()

main()