import json
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import sys

def plot_individual(filename):
    with open(filename, "r") as f:
        response_times_data = json.load(f)

    # Flatten the list of lists and create a DataFrame
    response_times = [time for client_times in response_times_data for time in client_times]
    response_times_df = pd.DataFrame(response_times, columns=["response_time"])

    # Plot histogram of response times
    response_times_df.plot.hist(grid=True, bins=20, rwidth=0.9)
    plt.title("Response Time Histogram")
    plt.xlabel("Response Time (s)")
    plt.ylabel("Frequency")
    plt.grid(axis="y", alpha=0.75)
    plt.show()

    # Create a DataFrame for client response times
    client_response_times_df = pd.DataFrame(response_times_data)

    # Calculate the average, min, and max response times for each request number
    average_response_times = client_response_times_df.mean()
    min_response_times = client_response_times_df.min()
    max_response_times = client_response_times_df.max()

    # Plot the average, min, and max response times
    plt.plot(average_response_times, label="Average")
    plt.plot(min_response_times, label="Min")
    plt.plot(max_response_times, label="Max")
    plt.title("Response Times per Request Number")
    plt.xlabel("Request Number")
    plt.ylabel("Response Time (s)")
    plt.legend(loc="upper right")
    plt.show()

def plot_multiple(filenames):
    # Read and process the response times data for each algorithm
    algorithm_response_times_data = []
    for file in filenames:
        with open(file, "r") as f:
            response_times_data = json.load(f)
            algorithm_response_times_data.append(response_times_data)

    # Flatten the list of lists and create DataFrames for each algorithm
    algorithm_response_times = []
    for response_times_data in algorithm_response_times_data:
        response_times = [time for client_times in response_times_data for time in client_times]
        algorithm_response_times.append(response_times)

    # Plot Kernel Density Estimation (KDE) for response times of each algorithm
    colors = ['blue', 'orange', 'green']
    labels = ['Baseline', 'Round Robin', 'Least Connections']

    for i, response_times in enumerate(algorithm_response_times):
        sns.kdeplot(response_times, color=colors[i], label=labels[i])

    plt.title("Response Time Distributions")
    plt.xlabel("Response Time (s)")
    plt.ylabel("Density")
    plt.legend(loc="upper right")
    plt.grid(axis="y", alpha=0.75)
    plt.show()

if __name__ == "__main__":
    if sys.argv[1] == '0':
        plot_individual(sys.argv[2])
    elif sys.argv[1] == '1':
        plot_multiple([
            "data/Baseline.json",
            "data/RoundRobin.json",
            "data/LeastConnections.json",
        ])

