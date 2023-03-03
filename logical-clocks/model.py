import sys
import socket
from _thread import*
import threading
import time, random

MESSAGE_QUEUE = []
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
    while True:
        msg = s.recv(1024)
        if not msg:
            return
        MESSAGE_QUEUE.append(msg)

def tick():
    pass

def main(machine_id):
    clock_speed = random.randint(1, 6)

    # TODO: this is really dirty but seems much less complicated to do it this way lol
    if machine_id == 1:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((HOST, PORTS[machine_id]))
        s.listen()

        while True:
            conn, addr = s.accept()
            print('Connected to: ' + addr[0] + ':' + str(addr[1]))
            start_new_thread(listen, (conn,))

    elif machine_id == 2:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((HOST, PORTS[machine_id]))
        s.listen()

        while True:
            err, s1 = get_socket(1)
            if err == 0:
                break

        start_new_thread(listen, (s1,))

        while True:
            conn, addr = s.accept()
            print('Connected to: ' + addr[0] + ':' + str(addr[1]))
            start_new_thread(listen, (conn,))

    elif machine_id == 3:
        s1 = None
        s2 = None
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

    start = time.time()
    period = 1.0 / clock_speed
    while True:
        if (time_time() - start) > period:
            start += period
            tick()

# TODO: naming wise, maybe this should be the main. leaving it out for now
if len(sys.argv) != 2:
    print("Must provide the process id argument")
    exit()

if not sys.argv[1].isdigit():
    print("process id argument must be an integer")
    exit()
else:
    process_id = int(sys.argv[1])
    if process_id in [1, 2, 3]:
        main(process_id)
    else:
        print("Must provide a valid process_id argument: 1, 2, 3")
        exit()
