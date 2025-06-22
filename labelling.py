import pandas as pd
import os

INPUT_FILE = "metrics_new.csv"
OUTPUT_FILE = "labeled_metrics_new.csv"

def label_data():
    try:
        df = pd.read_csv(INPUT_FILE)

        # Step 1: Assign base status
        df["status"] = "Normal"
        df.loc[df["cpu_usage"] > 90, "status"] = "High CPU Load"
        df.loc[df["memory_usage"] > 85, "status"] = "High Memory Usage"
        df.loc[df["process_cpu"] > 50, "status"] = "High Process Usage"

        # Step 2: Identify historically heavy apps (based on CPU and memory trends)
        cpu_heavy = (
            df[df["process_cpu"] > 30]
            .groupby("process_name")["process_cpu"]
            .mean()
        )
        mem_heavy = (
            df[df["process_memory"] > 10]
            .groupby("process_name")["process_memory"]
            .mean()
        )

        # Thresholds can be adjusted later
        historically_heavy_apps = set(cpu_heavy[cpu_heavy > 40].index) | set(mem_heavy[mem_heavy > 20].index)
        df["is_heavy_app"] = df["process_name"].isin(historically_heavy_apps)
        df.loc[df["is_heavy_app"], "status"] = "Historically Heavy App"

        # Step 3: Assign healing actions based on status
        healing_actions = {
            "High CPU Load": "Restart critical processes",
            "High Memory Usage": "Free memory, close unused apps",
            "High Process Usage": "Terminate high CPU processes",
            "Historically Heavy App": "Suggest close or offer alternative",
            "Normal": "No Action"
        }
        df["healing_action"] = df["status"].map(healing_actions)

        # Step 4: Save labeled data
        df.to_csv(OUTPUT_FILE, mode='w', header=True, index=False)
        print(f"✅ Dataset labeled and saved to {OUTPUT_FILE}")

    except Exception as e:
        print(f"❌ Labeling failed: {e}")

if __name__ == "__main__":
    label_data()
