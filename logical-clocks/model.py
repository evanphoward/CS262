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

LOG = -1
HOST = "127.0.0.1" # Being run on local host
PORTS = {1: 60000, 2: 60001, 3: 60002} # Ports for each machine

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

def listen(s):
    global MESSAGE_QUEUE
    while True:
        msg = s.recv(1024)
        if not msg:
            return
        try:
            receiving_time = int(msg.decode())
            QUEUE_LOCK.acquire()
            MESSAGE_QUEUE.append(receiving_time)
            QUEUE_LOCK.release()
        except ValueError:
            print("ValueError: Non-numeric message sent: " + msg)

def tick(s1, s2):
    global MESSAGE_QUEUE, CLOCK, LOG
    if MESSAGE_QUEUE:
        msg = MESSAGE_QUEUE.pop(0)
        CLOCK = max(msg, CLOCK) + 1
        action = "Received Message, " + str(len(MESSAGE_QUEUE)) + " messages remaining"
    else:
        opcode = random.randint(1, 10)
        if opcode == SEND_TO_ONE:
            # TODO: Have some identification of s1 and s2 for logging
            action = "Sent Message to 1"
            s1.sendall(str(CLOCK).encode())
        elif opcode == SEND_TO_TWO:
            action = "Sent Message to 2"
            s2.sendall(str(CLOCK).encode())
        elif opcode == SEND_TO_BOTH:
            action = "Sent Message to both processes"
            s1.sendall(str(CLOCK).encode())
            s2.sendall(str(CLOCK).encode())
        else:
            action = "Internal Event"
        CLOCK += 1
    print(time.strftime('%H:%M:%S', time.localtime()) + " / " + str(CLOCK) + ": " + action)
    LOG.write(time.strftime('%H:%M:%S', time.localtime()) + " / " + str(CLOCK) + ": " + action + "\n")

def initialize(machine_id):
    global LOG
    LOG = open("logs/log-" + str(machine_id), "w")

    # TODO: this is really dirty but seems much less complicated to do it this way lol
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
        sockets.append(s1)
        
    clock_speed = random.randint(1, 6)
    start = time.time()
    period = 1.0 / clock_speed
    LOG.write("Initialization Completed, Clock Speed " + str(clock_speed))
    while True:
        if (time.time() - start) > period:
            start += period
            tick(sockets[0], sockets[1])

def main():
    if len(sys.argv) != 2:
        print("Must provide the process id argument")
        return
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
