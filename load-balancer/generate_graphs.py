import json
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import sys

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
        response_times = []
        for client_times in response_times_data:
            for time in client_times:
                if time < 1:
                    response_times.append(time)
        algorithm_response_times.append(response_times)

    # Calculate the minimum and maximum values based on the filtered data
    min_value = min(min(response_times) for response_times in algorithm_response_times)
    max_value = max(max(response_times) for response_times in algorithm_response_times)
    print(min_value, max_value)

    # Plot histograms of response times for each algorithm
    colors = ['blue', 'orange', 'green']
    labels = ['Baseline', 'Round Robin', 'Least Connections']
    bins = np.linspace(min_value, max_value, 20)

    for i, response_times in enumerate(algorithm_response_times):
        plt.hist(response_times, bins=bins, alpha=0.5, color=colors[i], label=labels[i], density=True)

    plt.title("Response Time Histograms")
    plt.xlabel("Response Time (s)")
    plt.ylabel("Relative Frequency")
    plt.legend(loc="upper right")
    plt.grid(axis="y", alpha=0.75)
    plt.show()

if __name__ == "__main__":
    plot_multiple([
        "data/Baseline.json",
        "data/RoundRobin.json",
        "data/LeastConnections.json",
    ])

