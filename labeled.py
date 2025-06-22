import pandas as pd
import os

INPUT_FILE = "metrics.csv"
OUTPUT_FILE = "labeled_metrics.csv"

try:
    df = pd.read_csv(INPUT_FILE)

    df["status"] = "Normal"

    df.loc[df["cpu_usage"] > 90, "status"] = "High CPU Load"
    df.loc[df["memory_usage"] > 85, "status"] = "High Memory Usage"
    df.loc[df["process_cpu"] > 50, "status"] = "High Process Usage"

    healing_actions = {
        "High CPU Load": "Restart critical processes",
        "High Memory Usage": "Free memory, close unused apps",
        "High Process Usage": "Terminate high CPU processes",
        "Normal": "No Action"
    }

    df["healing_action"] = df["status"].map(healing_actions)

    df.to_csv(OUTPUT_FILE, mode='a', header=not os.path.exists(OUTPUT_FILE), index=False)

    print(f"Dataset labeled and appended to {OUTPUT_FILE}")

except Exception as e:
    print(f"Error processing dataset: {e}")
