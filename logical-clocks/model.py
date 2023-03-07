import sys
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

TIME_LIMIT_S = 90

HOST = "127.0.0.1" # Being run on local host
PORTS = {1: 60000, 2: 60001, 3: 60002} # Ports for each machine

""" Function that connects to port of specificed process id """
def get_socket(id):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((HOST, PORTS[id]))
        return 0, s
    except ConnectionRefusedError:
        return 1, "Connection Refused Error"
    except TimeoutError:
        return 1, "Timeout Error"
    except:
        return 2, "Server Connection Error"

""" Function that listens for messages and add messages to the queue """
def listen(s):
    global MESSAGE_QUEUE
    while True:
        msg = s.recv(1024)
        if not msg:
            return
        try:
            QUEUE_LOCK.acquire()
            MESSAGE_QUEUE.append(int(msg.decode()))
            QUEUE_LOCK.release()
        except ValueError:
            print("ValueError: Non-numeric message sent: " + msg)


""" Helper function that takes a message from the queue and syncs the local clock """
def get_message(queue, clock):
    QUEUE_LOCK.acquire()
    msg = queue.pop(0)
    QUEUE_LOCK.release()
    new_clock = max(msg, clock) + 1
    action = "Received Message, " + str(len(queue)) + " messages remaining"
    return new_clock, action

""" Helper function that chooses connections to send to based on the op_code """
def perform_op(opcode):
    if opcode == SEND_TO_ONE:
        # TODO: Have some identification of s1 and s2 for logging
        action = "Sent Message to 1"
        send_s1 = True
        send_s2 = False
    elif opcode == SEND_TO_TWO:
        action = "Sent Message to 2"
        send_s1 = False
        send_s2 = True
    elif opcode == SEND_TO_BOTH:
        action = "Sent Message to both processes"
        send_s1 = True
        send_s2 = True
    else:
        action = "Internal Event"
        send_s1 = False
        send_s2 = False
    return action, send_s1, send_s2

""" Function that performs a tick on a given process and logs the result """
def tick(s1, s2, log_txt, log_csv):
    global MESSAGE_QUEUE, CLOCK
    opcode = 0

    # If there is a message in the queue, read the message and sync the clock
    if MESSAGE_QUEUE:
        CLOCK, action = get_message(MESSAGE_QUEUE, CLOCK)
    # Otherwise, randomly perform a send to another machine(s)
    else:
        opcode = random.randint(1, 10)
        action, send_s1, send_s2 = perform_op(opcode)
        if send_s1:
            s1.sendall(str(CLOCK).encode())
        if send_s2:
            s2.sendall(str(CLOCK).encode())
        CLOCK += 1
    print(time.strftime('%H:%M:%S', time.localtime()) + " / " + str(CLOCK) + ": " + action)
    log_txt.write(time.strftime('%H:%M:%S', time.localtime()) + " / " + str(CLOCK) + ": " + action + "\n")
    log_csv.write("{},{},{},{}\n".format(time.strftime('%H:%M:%S', time.localtime()), str(CLOCK), opcode, len(MESSAGE_QUEUE)))

""" Function that initializes the machine by connecting to other machines """
def initialize(machine_id):
    log_txt = open("logs/log-" + str(machine_id), "w")
    log_csv = open("logs/log-" + str(machine_id) + ".csv", "w")
    log_csv.write("System Clock,Logical Clock,Action,Messages Remaining\n")

    sockets = []

    # machine 1 waits for 2 connections
    if machine_id == 1:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((HOST, PORTS[machine_id]))
        s.listen()

        conns = 0
        while conns < 2:
            conn, addr = s.accept()
            print('Connected to: ' + addr[0] + ':' + str(addr[1]))
            start_new_thread(listen, (conn,))
            sockets.append(conn)
            conns += 1

    # machine 2 connects to machine 1 and waits for 1 connection
    elif machine_id == 2:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((HOST, PORTS[machine_id]))
        s.listen()

        while True:
            err, s1 = get_socket(1)
            if err == 0:
                break

        start_new_thread(listen, (s1,))
        sockets.append(s1)

        conns = 0
        while conns < 1:
            conn, addr = s.accept()
            print('Connected to: ' + addr[0] + ':' + str(addr[1]))
            start_new_thread(listen, (conn,))
            sockets.append(conn)
            conns += 1

    # machine 3 connects to machine 1 and machine 2
    elif machine_id == 3:
        while True:
            err, s1 = get_socket(1)
            if err == 0:
                break

        while True:
            err, s2 = get_socket(2)
            if err == 0:
                break

        start_new_thread(listen, (s1,))
        start_new_thread(listen, (s2,))
        sockets.append(s1)
        sockets.append(s2)

    # Determine clock speed via random and start ticking
    clock_speed = random.randint(1, 6)
    start = time.time()
    start_prog = time.time()
    period = 1.0 / clock_speed
    log_txt.write("Initialization Completed, Clock Speed " + str(clock_speed) + "\n")
    try:
        time.sleep(machine_id / 100)
        while True:
            if (time.time() - start) > period:
                start += period
                tick(sockets[0], sockets[1], log_txt, log_csv)
                if(time.time() - start_prog) > TIME_LIMIT_S:
                    break
    finally:
        log_txt.close()
        log_csv.close()

""" Function for running unit tests """
def unit_tests():
    # Tests to get message from queue for singleton queue
    clock, _ = get_message([4], 3)
    assert(clock == 5)
    clock, _ = get_message([5], 6)
    assert(clock == 7)
    clock, _ = get_message([6], 6)
    assert(clock == 7)

    # Tests consecutive getting of message from one queue
    queue = [2, 4, 6, 9]
    clock, _ = get_message(queue, 1)
    assert(clock == 3)
    clock, _ = get_message(queue, 5)
    assert(clock == 6)
    clock, _ = get_message(queue, 6)
    assert(clock == 7)
    clock, _ = get_message(queue, 10)
    assert(clock == 11)

    # Tests for performing operation based on opcode
    _, send_s1, send_s2 = perform_op(SEND_TO_ONE)
    assert (send_s1 and not send_s2)
    _, send_s1, send_s2 = perform_op(SEND_TO_TWO)
    assert (not send_s1 and send_s2)
    _, send_s1, send_s2 = perform_op(SEND_TO_BOTH)
    assert (send_s1 and send_s2)
    _, send_s1, send_s2 = perform_op(5)
    assert (not send_s1 and not send_s2)

""" main function. should be called from command line with one argument (1, 2, 3) referring to process id or test argument to run unit tests """
def main():
    if len(sys.argv) != 2:
        print("Must provide the process id argument or unit test argument")
        return
    if sys.argv[1] == "test":
        unit_tests()
        print("passes all unit tests")
        exit()
    if not sys.argv[1].isdigit():
        print("process id argument must be an integer")
        return

    process_id = int(sys.argv[1])
    if process_id in [1, 2, 3]:
        initialize(process_id)
    else:
        print("Must provide a valid process_id argument: 1, 2, 3")
        exit()

main()
