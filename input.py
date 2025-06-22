import pandas as pd
import time
import os
from prometheus_api_client import PrometheusConnect

# File to store metrics
FILE_PATH = "metrics1.csv"

# Connect to Prometheus
PROMETHEUS_URL = "http://localhost:9090"  # Update if Prometheus runs elsewhere
prom = PrometheusConnect(url=PROMETHEUS_URL, disable_ssl=True)

def get_system_metrics():
    """Fetch system-wide CPU and Memory usage from Prometheus."""
    cpu_query = '100 - (avg by (instance) (rate(windows_cpu_time_total{mode="idle"}[1m])) * 100)'
    mem_query = '100 * (1 - (windows_memory_commit_limit - windows_memory_committed_bytes) / windows_memory_commit_limit)'

    cpu_usage = prom.custom_query(query=cpu_query)
    memory_usage = prom.custom_query(query=mem_query)

    # Extract values
    cpu_value = float(cpu_usage[0]['value'][1]) if cpu_usage else 0
    memory_value = float(memory_usage[0]['value'][1]) if memory_usage else 0

    return cpu_value, memory_value

def get_running_processes():
    """Fetch active processes and their CPU/Memory usage from Prometheus."""
    cpu_query = 'rate(windows_process_cpu_seconds_total[1m])'
    mem_query = 'windows_process_private_usage_bytes'

    cpu_data = prom.custom_query(query=cpu_query)
    mem_data = prom.custom_query(query=mem_query)

    process_dict = {}

    # Process CPU Usage
    for process in cpu_data:
        pid = process["metric"].get("process_id", "unknown")
        name = process["metric"].get("process", "unknown")
        cpu = float(process["value"][1])

        process_dict[pid] = {
            "name": name,
            "cpu": cpu,
            "memory": 0  # Placeholder for memory
        }

    # Process Memory Usage
    for process in mem_data:
        pid = process["metric"].get("process_id", "unknown")
        memory = float(process["value"][1]) / (1024 * 1024)  # Convert bytes to MB

        if pid in process_dict:
            process_dict[pid]["memory"] = memory

    # Convert dictionary to list
    process_list = [[pid, data["name"], data["cpu"], data["memory"]] for pid, data in process_dict.items()]

    return process_list

def log_metrics():
    """Log system metrics and running process data to CSV."""
    columns = ["timestamp", "cpu_usage", "memory_usage", "process_name", "pid", "process_cpu", "process_memory"]

    while True:
        timestamp = int(time.time())
        cpu_usage, memory_usage = get_system_metrics()
        processes = get_running_processes()

        # Prepare data
        data = []
        for pid, name, process_cpu, process_mem in processes:
            data.append([timestamp, cpu_usage, memory_usage, name, pid, process_cpu, process_mem])

        # Save data to CSV
        df = pd.DataFrame(data, columns=columns)
        df.to_csv(FILE_PATH, mode='a', header=not os.path.exists(FILE_PATH), index=False)

        print(f"✅ Logged {len(data)} processes at {timestamp}")

        time.sleep(5)  # Adjust data collection frequency

if __name__ == "__main__":
    log_metrics()
