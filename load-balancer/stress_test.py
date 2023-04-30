import sys
import concurrent.futures
import json
import random
import time
from client import Client

def make_requests(number_of_requests):
    client = Client()
    response_times = []
    for _ in range(number_of_requests):
        response, response_time = client.send_request(b"PING!")
        response_times.append(response_time)
    return response_times

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("How to Use: python3 stress_test.py [number_of_clients] [max_number_of_requests]")
        exit()

    number_of_clients = int(sys.argv[1])
    max_number_of_requests = int(sys.argv[2])

    # Start multiple clients concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=number_of_clients) as executor:
        start_time = time.time()
        results = list(executor.map(make_requests, [random.randint(1, max_number_of_requests)] * number_of_clients))
        with open("response_times.json", "w") as f:
            json.dump(results, f)
        print(f"Total time: {time.time() - start_time} seconds")
        