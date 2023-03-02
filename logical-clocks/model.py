import time, random

def tick():

def main():
    clock_speed = random.randint(1, 6)

    start = time.time()
    period = 1.0 / clock_speed
    while True:
        if (time_time() - start) > period:
            start += period
            tick()

main()