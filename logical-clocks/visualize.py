import sys
import pandas as pd
from matplotlib import pyplot as plt

def analyze(dir):
    log1_df = pd.read_csv(dir + "log-1.csv")
    log2_df = pd.read_csv(dir + "log-2.csv")
    log3_df = pd.read_csv(dir + "log-3.csv")

    for df in [log1_df, log2_df, log3_df]:
        length = len(df.index)
        df["Universal Time"] = df.index / length

    plt.rcParams["figure.figsize"] = [20.00, 10.00]
    plt.rcParams["figure.autolayout"] = True

    ax = log1_df.plot(x = 'Universal Time', y = 'Logical Clock', label = "machine1")
    log2_df.plot(ax = ax, x = 'Universal Time', y = 'Logical Clock', label = "machine2")
    log3_df.plot(ax = ax, x = 'Universal Time', y = 'Logical Clock', label = "machine3")
    plt.savefig(dir + "clock.png")

    plt.rcParams["figure.figsize"] = [10.00, 6.00]
    ax = log1_df.plot(x = 'Universal Time', y = 'Messages Remaining', label = "machine1")
    log2_df.plot(ax = ax, x = 'Universal Time', y = 'Messages Remaining', label = "machine2")
    log3_df.plot(ax = ax, x = 'Universal Time', y = 'Messages Remaining', label = "machine3")
    plt.savefig(dir + "messages.png")

def main():
    if len(sys.argv) != 2:
        print("Must provide directory")
    analyze(sys.argv[1])

main()
