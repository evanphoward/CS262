# CS262-logical-clock
Design Project 2: Logical Clock, CS 262 Spring 2023\
This is a simulation of three separate processes running and sending messages to each other with a logical clock. This simulates a small asynchronous distributed system, each of which runs at a different speed.

# How to Use
You can start the first process by running the following command in the directory:
```console
python3 model.py 1
```

You can start the second process by running the following command in the directory:
```console
python3 model.py 2
```

You can start the third process by running the following command in the directory:
```console
python3 model.py 3
```

Once the third process gets started, it should have connected to the first two processes and each machine should start ticking.\
Note: Processes must be started in the above order in order to accurately simulate the asynchronous distributed system. Do not start process 2 before process 1 or process 3 before process 1 / 2.

Once the processes start running, they will run for 90 seconds and leave log files in logs/. The time can be adjusted using the TIME_LIMIT_S variable in model.py

# How to Analyze Model
Let [dir] be the directory that the log text and csv files are saved. One can analyze the results of the model by running the following command:
```console
python3 visualize.py [dir]
```
Running the command will create two png files in [dir]. [dir]/clock.png will be a graph that plots the logical clock progression of all three machines. [dir]/messages.png will be a graph that plots the remaining messages progression of all three machines.

# Analysis
The results of our analysis could be found in journals/combined-analysis.md

# How to Test
In order to run unit tests, run the following command in the directory:
```console
python3 model.py test
```

Running the command will run a series of unit tests on the model. If all unit tests pass, you will get an indicator that all messages have passed. If a unit test fails, you will get an assertion error and which line the unit tests failed on.

# Functionality
- machine's clock rate determined at initialization
- machines connect to two other machines at initialization
- machine has message queue that it reads from and updates the logical clock
- if there are no messages in the message queue, machine sends messages to one or both machines or does an internal event
- machine logs all operations and the logical clock time in this process
